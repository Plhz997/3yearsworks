from flask import Blueprint, request, jsonify
from models.vocabulary import Vocabulary
from models.wrong_word import WrongWord
from models.pomodoro_record import PomodoroRecord
from app import db
from utils.llm_task_matcher import match_learning_task

pomodoro_bp = Blueprint('pomodoro', __name__)

def get_user_id_from_request():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        import jwt
        import json
        from config.config import Config
        decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
        sub = decoded.get('sub')
        if isinstance(sub, str):
            try:
                sub = json.loads(sub)
            except Exception:
                pass
        if isinstance(sub, dict) and sub.get('type') == 'user':
            return sub.get('user_id')
        return decoded.get('user_id')
    except Exception as exc:
        print(f"Failed to parse token: {exc}")
        return None

def word_to_task_item(word):
    data = word.to_dict()
    data['keywords'] = [part.strip() for part in word.meaning.replace('，', ',').split(',') if part.strip()]
    return data

@pomodoro_bp.route('/groups', methods=['GET'])
def get_groups():
    user_id = get_user_id_from_request()
    wrong_count = 0
    if user_id:
        wrong_count = WrongWord.query.filter_by(user_id=user_id).count()
    return jsonify({
        'success': True,
        'groups': [
            {'id': 'level_1', 'name': '小学高频词汇', 'desc': '基础新词和日常词汇'},
            {'id': 'level_2', 'name': '初中高频词汇', 'desc': '核心常用词汇'},
            {'id': 'level_3', 'name': '高中高频词汇', 'desc': '进阶阅读词汇'},
            {'id': 'wrong', 'name': '我的错词本', 'desc': f'{wrong_count} 个待复习错词'}
        ]
    }), 200

@pomodoro_bp.route('/start', methods=['POST'])
def start_pomodoro_task():
    data = request.get_json() or {}
    user_id = get_user_id_from_request()
    group = data.get('group', 'level_2')
    task_type = data.get('task_type', 'wrong')
    limit = min(int(data.get('limit', 20)), 50)

    if group == 'wrong' or task_type == 'wrong':
        words = []
        if user_id:
            wrong_words = WrongWord.query.filter_by(user_id=user_id).order_by(WrongWord.last_wrong_time.desc()).limit(limit).all()
            ids = [item.word_id for item in wrong_words]
            words = Vocabulary.query.filter(Vocabulary.id.in_(ids)).all() if ids else []
        if not words:
            words = Vocabulary.query.order_by(Vocabulary.difficulty.desc()).limit(limit).all()
    else:
        level = int(group.replace('level_', '')) if group.startswith('level_') else 2
        query = Vocabulary.query.filter_by(level=level)
        if task_type == 'new':
            query = query.order_by(Vocabulary.frequency.desc())
        elif task_type == 'spell':
            query = query.order_by(Vocabulary.difficulty.desc())
        else:
            query = query.order_by(db.func.random())
        words = query.limit(limit).all()

    return jsonify({
        'success': True,
        'words': [word_to_task_item(word) for word in words],
        'group': group,
        'task_type': task_type
    }), 200

@pomodoro_bp.route('/match-task', methods=['POST'])
def match_pomodoro_task():
    data = request.get_json() or {}
    task_type = data.get('task_type', 'reading')
    level = data.get('level', '高中')
    topic = data.get('topic', '日常学习')
    weakness = data.get('weakness', '')
    count = min(int(data.get('count', 5)), 8)
    task = match_learning_task(task_type, level, topic, weakness, count)
    return jsonify({
        'success': True,
        'task': task
    }), 200

@pomodoro_bp.route('/submit', methods=['POST'])
def submit_pomodoro_task():
    data = request.get_json() or {}
    user_id = get_user_id_from_request()
    results = data.get('results', [])
    completed_count = len(results)
    correct_count = len([item for item in results if item.get('is_correct')])
    accuracy = correct_count / completed_count if completed_count else 0
    duration_seconds = int(data.get('duration_seconds', 0))
    target_count = int(data.get('target_count', completed_count))

    wrong_results = [item for item in results if not item.get('is_correct') and item.get('word_id')]
    if user_id:
        for item in wrong_results:
            wrong_word = WrongWord.query.filter_by(user_id=user_id, word_id=item['word_id']).first()
            if wrong_word:
                wrong_word.wrong_count += 1
                wrong_word.last_wrong_time = db.func.current_timestamp()
            else:
                db.session.add(WrongWord(user_id=user_id, word_id=item['word_id']))

    beans = max(3, completed_count // 2 + int(accuracy * 5))
    energy = max(5, completed_count + int(accuracy * 10))
    recommendation = build_recommendation(accuracy, wrong_results, data.get('task_type', 'wrong'))

    record = PomodoroRecord(
        user_id=user_id,
        word_group=data.get('group', 'level_2'),
        task_type=data.get('task_type', 'wrong'),
        duration_seconds=duration_seconds,
        target_count=target_count,
        completed_count=completed_count,
        correct_count=correct_count,
        accuracy=accuracy,
        coffee_beans=beans,
        energy_value=energy,
        recommendation=recommendation
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        'success': True,
        'record': record.to_dict(),
        'wrong_count': len(wrong_results),
        'coffee_beans': beans,
        'energy_value': energy,
        'recommendation': recommendation
    }), 200

def build_recommendation(accuracy, wrong_results, task_type):
    study_recommendations = {
        'reading': '阅读完成后，下一轮建议做七选五，继续训练段落逻辑和同义替换。',
        'cloze7': '七选五完成后，下一轮建议做阅读理解，把上下文衔接能力迁移到长文章。',
        'listening': '精听完成后，下一轮建议做影子跟读，巩固刚刚听到的语音和词块。',
        'shadowing': '影子跟读完成后，下一轮建议做英语精听，检查自己是否真正听清。'
    }
    if task_type in study_recommendations:
        if accuracy < 0.8:
            return '这轮还有步骤没完成，下一轮建议开 10 分钟轻量任务把剩余步骤补完。'
        return study_recommendations[task_type]
    if wrong_results:
        return f'下一轮建议复习 {len(wrong_results)} 个错词，优先做错词复习。'
    if accuracy >= 0.9:
        return '这一轮掌握很好，下一轮可以切换到新词学习或提升词库难度。'
    if task_type == 'spell':
        return '拼写还可以继续巩固，下一轮建议做 10 个拼写训练。'
    return '建议下一轮做 10 题单词测评，检查刚刚的记忆效果。'
