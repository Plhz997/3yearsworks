from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.test_record import TestRecord
from models.test_detail import TestDetail
from models.wrong_word import WrongWord
from models.vocabulary import Vocabulary
from utils.test_algorithm import TestAlgorithm, SmartTestAlgorithm, StandardTestAlgorithm
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
def start_smart_test():
    user_id = None
    
    auth_header = request.headers.get('Authorization', '')
    print(f"Authorization header: {auth_header}")
    
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            import jwt
            import json
            from config.config import Config
            decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
            print(f"Decoded token: {decoded}")
            
            if decoded.get('sub'):
                sub = decoded['sub']
                if isinstance(sub, str):
                    try:
                        sub = json.loads(sub)
                    except:
                        pass
                if isinstance(sub, dict):
                    if sub.get('type') == 'user':
                        user_id = sub.get('user_id')
        
            if not user_id and decoded.get('user_id'):
                user_id = decoded['user_id']
            
            print(f"Parsed user_id: {user_id}")
        except Exception as e:
            print(f"Failed to parse token: {e}")
    
    if not user_id:
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    data = request.get_json()
    level = data.get('level', 2)
    
    algorithm = SmartTestAlgorithm(db.session, user_id)
    words = algorithm.get_personalized_words(level, 20)
    questions = []
    
    for word in words:
        question = algorithm.generate_question(word)
        question['level'] = word['level']
        questions.append(question)
    
    return jsonify({'success': True, 'questions': questions}), 200

@test_bp.route('/start/standard', methods=['POST'])
def start_standard_test():
    algorithm = StandardTestAlgorithm(db.session)
    words = algorithm.get_standard_words()
    questions = []
    
    for word in words:
        question = algorithm.generate_question_with_options(word)
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
    
    auth_header = request.headers.get('Authorization', '')
    print(f"Authorization header: {auth_header}")
    
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            import jwt
            import json
            from config.config import Config
            decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
            print(f"Decoded token: {decoded}")
            
            if decoded.get('sub'):
                sub = decoded['sub']
                if isinstance(sub, str):
                    try:
                        sub = json.loads(sub)
                    except:
                        pass
                if isinstance(sub, dict):
                    if sub.get('type') == 'user':
                        user_id = sub.get('user_id')
            
            if not user_id and decoded.get('user_id'):
                user_id = decoded['user_id']
            
            print(f"Parsed user_id: {user_id}")
        except Exception as e:
            print(f"Failed to parse token: {e}")
    
    print(f"Submit test - user_id: {user_id}, level: {level}, results count: {len(results)}")
    
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
def get_records():
    user_id = None
    
    auth_header = request.headers.get('Authorization', '')
    print(f"Get records - Authorization header: {auth_header}")
    
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            import jwt
            import json
            from config.config import Config
            decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
            print(f"Decoded token: {decoded}")
            
            if decoded.get('sub'):
                sub = decoded['sub']
                if isinstance(sub, str):
                    try:
                        sub = json.loads(sub)
                    except:
                        pass
                if isinstance(sub, dict):
                    if sub.get('type') == 'user':
                        user_id = sub.get('user_id')
            
            if not user_id and decoded.get('user_id'):
                user_id = decoded['user_id']
            
            print(f"Parsed user_id: {user_id}")
        except Exception as e:
            print(f"Failed to parse token: {e}")
    
    if not user_id:
        return jsonify({'success': True, 'records': []}), 200
    
    records = TestRecord.query.filter_by(user_id=user_id).order_by(TestRecord.created_at.desc()).all()
    
    return jsonify({'success': True, 'records': [r.to_dict() for r in records]}), 200

@test_bp.route('/record/<int:record_id>', methods=['GET'])
def get_record_detail(record_id):
    user_id = None
    
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            import jwt
            import json
            from config.config import Config
            decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
            
            if decoded.get('sub'):
                sub = decoded['sub']
                if isinstance(sub, str):
                    try:
                        sub = json.loads(sub)
                    except:
                        pass
                if isinstance(sub, dict):
                    if sub.get('type') == 'user':
                        user_id = sub.get('user_id')
            
            if not user_id and decoded.get('user_id'):
                user_id = decoded['user_id']
        except Exception as e:
            print(f"Failed to parse token: {e}")
    
    if not user_id:
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    record = TestRecord.query.get(record_id)
    if not record:
        return jsonify({'success': False, 'message': '记录不存在'}), 404
    
    if record.user_id != user_id:
        return jsonify({'success': False, 'message': '无权访问此记录'}), 403
    
    details = TestDetail.query.filter_by(record_id=record_id).all()
    
    return jsonify({
        'success': True,
        'record': record.to_dict(),
        'details': [d.to_dict() for d in details]
    }), 200