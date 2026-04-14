from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.test_record import TestRecord
from models.test_detail import TestDetail
from models.wrong_word import WrongWord
from models.vocabulary import Vocabulary
from utils.test_algorithm import TestAlgorithm, SmartTestAlgorithm
from app import db

test_bp = Blueprint('test', __name__)

@test_bp.route('/start', methods=['POST'])
def start_test():
    data = request.get_json()
    level = data.get('level', 2)
    mode = data.get('mode', 'basic')
    
    algorithm = TestAlgorithm(db.session)
    if mode == 'smart':
        algorithm = SmartTestAlgorithm(db.session)
    
    words = algorithm.get_mixed_words(level, 20)
    questions = []
    
    for word in words:
        question = algorithm.generate_question(word)
        question['level'] = word['level']
        questions.append(question)
    
    return jsonify({'success': True, 'questions': questions}), 200

@test_bp.route('/start/smart', methods=['POST'])
@jwt_required()
def start_smart_test():
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    data = request.get_json()
    level = data.get('level', 2)
    
    algorithm = SmartTestAlgorithm(db.session, identity['user_id'])
    words = algorithm.get_personalized_words(level, 20)
    questions = []
    
    for word in words:
        question = algorithm.generate_question(word)
        question['level'] = word['level']
        questions.append(question)
    
    return jsonify({'success': True, 'questions': questions}), 200

@test_bp.route('/submit', methods=['POST'])
def submit_test():
    data = request.get_json()
    results = data.get('results', [])
    level = data.get('level', 2)
    
    algorithm = TestAlgorithm(db.session)
    analysis = algorithm.analyze_results(results)
    estimated_level = algorithm.estimate_level(results)
    
    user_id = None
    identity = None
    try:
        from flask_jwt_extended import get_jwt_identity
        identity = get_jwt_identity()
        if identity and identity.get('type') == 'user':
            user_id = identity['user_id']
    except:
        pass
    
    record = TestRecord(
        user_id=user_id,
        level=level,
        total_count=analysis['overall']['total'],
        correct_count=analysis['overall']['correct'],
        accuracy=analysis['overall']['accuracy'],
        estimated_level=estimated_level
    )
    db.session.add(record)
    db.session.commit()
    
    for result in results:
        detail = TestDetail(
            record_id=record.id,
            word_id=result['word_id'],
            word=result['word'],
            meaning=result['meaning'],
            user_answer=result.get('user_answer'),
            is_correct=1 if result['is_correct'] else 0,
            time_spent=result.get('time_spent'),
            question_type=result.get('question_type')
        )
        db.session.add(detail)
        
        if not result['is_correct'] and user_id:
            wrong_word = WrongWord.query.filter_by(user_id=user_id, word_id=result['word_id']).first()
            if wrong_word:
                wrong_word.wrong_count += 1
                wrong_word.last_wrong_time = db.func.current_timestamp()
            else:
                wrong_word = WrongWord(user_id=user_id, word_id=result['word_id'])
                db.session.add(wrong_word)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'record_id': record.id,
        'analysis': analysis,
        'estimated_level': estimated_level,
        'level_name': algorithm.LEVEL_NAMES.get(estimated_level, '未知')
    }), 200

@test_bp.route('/records', methods=['GET'])
@jwt_required()
def get_records():
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    user_id = identity['user_id']
    records = TestRecord.query.filter_by(user_id=user_id).order_by(TestRecord.created_at.desc()).all()
    
    return jsonify({'success': True, 'records': [r.to_dict() for r in records]}), 200

@test_bp.route('/record/<int:record_id>', methods=['GET'])
@jwt_required()
def get_record_detail(record_id):
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    record = TestRecord.query.get(record_id)
    if not record:
        return jsonify({'success': False, 'message': '记录不存在'}), 404
    
    details = TestDetail.query.filter_by(record_id=record_id).all()
    
    return jsonify({
        'success': True,
        'record': record.to_dict(),
        'details': [d.to_dict() for d in details]
    }), 200