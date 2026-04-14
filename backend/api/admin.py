from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.admin import Admin
from models.test_record import TestRecord
from models.vocabulary import Vocabulary
from app import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    keyword = request.args.get('keyword', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = User.query
    if keyword:
        query = query.filter(User.username.ilike(f'%{keyword}%') | User.email.ilike(f'%{keyword}%'))
    
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    
    users = []
    for user in pagination.items:
        user_dict = user.to_dict()
        records = TestRecord.query.filter_by(user_id=user.id).all()
        user_dict['test_count'] = len(records)
        user_dict['avg_accuracy'] = sum(r.accuracy for r in records) / len(records) if records else 0
        users.append(user_dict)
    
    return jsonify({
        'success': True,
        'data': users,
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '删除成功'}), 200

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    user_count = User.query.count()
    vocab_count = Vocabulary.query.count()
    test_count = TestRecord.query.count()
    
    level_distribution = {}
    for level in [1, 2, 3]:
        level_distribution[level] = Vocabulary.query.filter_by(level=level).count()
    
    recent_tests = TestRecord.query.order_by(TestRecord.created_at.desc()).limit(10).all()
    
    return jsonify({'success': True, 'stats': {
        'user_count': user_count,
        'vocab_count': vocab_count,
        'test_count': test_count,
        'level_distribution': level_distribution,
        'recent_tests': [r.to_dict() for r in recent_tests]
    }}), 200