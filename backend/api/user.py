from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.wrong_word import WrongWord
from models.favorite import Favorite
from models.vocabulary import Vocabulary
from models.test_record import TestRecord
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/wrong_words', methods=['GET'])
def get_wrong_words():
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
        return jsonify({'success': True, 'data': []}), 200
    
    wrong_words = WrongWord.query.filter_by(user_id=user_id).order_by(WrongWord.last_wrong_time.desc()).all()
    
    result = []
    for ww in wrong_words:
        word = Vocabulary.query.get(ww.word_id)
        if word:
            item = word.to_dict()
            item['wrong_count'] = ww.wrong_count
            item['last_wrong_time'] = ww.last_wrong_time.strftime('%Y-%m-%d %H:%M:%S') if ww.last_wrong_time else None
            result.append(item)
    
    return jsonify({'success': True, 'data': result}), 200

@user_bp.route('/wrong_words/<int:word_id>', methods=['DELETE'])
@jwt_required()
def remove_wrong_word(word_id):
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    user_id = identity['user_id']
    wrong_word = WrongWord.query.filter_by(user_id=user_id, word_id=word_id).first()
    
    if not wrong_word:
        return jsonify({'success': False, 'message': '记录不存在'}), 404
    
    db.session.delete(wrong_word)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已从错题本移除'}), 200

@user_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    user_id = identity['user_id']
    favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()).all()
    
    result = []
    for fav in favorites:
        word = Vocabulary.query.get(fav.word_id)
        if word:
            result.append(word.to_dict())
    
    return jsonify({'success': True, 'data': result}), 200

@user_bp.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    data = request.get_json()
    word_id = data.get('word_id')
    
    if not word_id:
        return jsonify({'success': False, 'message': '缺少单词ID'}), 400
    
    user_id = identity['user_id']
    favorite = Favorite.query.filter_by(user_id=user_id, word_id=word_id).first()
    
    if favorite:
        return jsonify({'success': False, 'message': '已收藏'}), 400
    
    new_favorite = Favorite(user_id=user_id, word_id=word_id)
    db.session.add(new_favorite)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '收藏成功'}), 201

@user_bp.route('/favorites/<int:word_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(word_id):
    identity = get_jwt_identity()
    if identity.get('type') != 'user':
        return jsonify({'success': False, 'message': '需要登录'}), 401
    
    user_id = identity['user_id']
    favorite = Favorite.query.filter_by(user_id=user_id, word_id=word_id).first()
    
    if not favorite:
        return jsonify({'success': False, 'message': '记录不存在'}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已取消收藏'}), 200

@user_bp.route('/stats', methods=['GET'])
def get_user_stats():
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
        return jsonify({'success': True, 'stats': {
            'total_tests': 0,
            'avg_accuracy': 0,
            'last_test_date': None,
            'level_distribution': {}
        }}), 200
    
    records = TestRecord.query.filter_by(user_id=user_id).all()
    
    if not records:
        return jsonify({'success': True, 'stats': {
            'total_tests': 0,
            'avg_accuracy': 0,
            'last_test_date': None,
            'level_distribution': {}
        }}), 200
    
    total_tests = len(records)
    avg_accuracy = sum(r.accuracy for r in records) / total_tests
    last_test_date = max(r.created_at for r in records).strftime('%Y-%m-%d')
    
    level_distribution = {}
    for record in records:
        level = record.level
        if level not in level_distribution:
            level_distribution[level] = {'count': 0, 'avg_accuracy': 0}
        level_distribution[level]['count'] += 1
        level_distribution[level]['avg_accuracy'] += record.accuracy
    
    for level in level_distribution:
        level_distribution[level]['avg_accuracy'] /= level_distribution[level]['count']
    
    return jsonify({'success': True, 'stats': {
        'total_tests': total_tests,
        'avg_accuracy': round(avg_accuracy, 2),
        'last_test_date': last_test_date,
        'level_distribution': level_distribution
    }}), 200