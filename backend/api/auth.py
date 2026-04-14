from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.admin import Admin
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '注册成功', 'user': new_user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity={'user_id': user.id, 'username': username, 'type': 'user'})
        return jsonify({'success': True, 'message': '登录成功', 'access_token': access_token, 'user': user.to_dict()}), 200
    
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.query.filter_by(username=username).first()
    
    if admin and check_password_hash(admin.password, password):
        access_token = create_access_token(identity={'admin_id': admin.id, 'username': username, 'type': 'admin'})
        return jsonify({'success': True, 'message': '管理员登录成功', 'access_token': access_token, 'admin': admin.to_dict()}), 200
    
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    identity = get_jwt_identity()
    if identity.get('type') == 'user':
        user = User.query.get(identity['user_id'])
        if user:
            return jsonify({'success': True, 'user': user.to_dict()}), 200
    return jsonify({'success': False, 'message': '用户未找到'}), 404