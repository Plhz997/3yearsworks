from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.vocabulary import Vocabulary
from models.favorite import Favorite
from models.wrong_word import WrongWord
from app import db
import csv
import io

vocab_bp = Blueprint('vocab', __name__)

@vocab_bp.route('/list', methods=['GET'])
def get_vocab_list():
    level = request.args.get('level', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Vocabulary.query
    if level:
        query = query.filter_by(level=level)
    
    pagination = query.order_by(Vocabulary.level, Vocabulary.frequency.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        'data': [v.to_dict() for v in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }), 200

@vocab_bp.route('/search', methods=['GET'])
def search_vocab():
    keyword = request.args.get('keyword', '')
    level = request.args.get('level', type=int)
    
    query = Vocabulary.query
    if keyword:
        query = query.filter(Vocabulary.word.ilike(f'%{keyword}%') | Vocabulary.meaning.ilike(f'%{keyword}%'))
    if level:
        query = query.filter_by(level=level)
    
    words = query.all()
    
    return jsonify({'success': True, 'data': [v.to_dict() for v in words]}), 200

@vocab_bp.route('/<int:word_id>', methods=['GET'])
def get_word_detail(word_id):
    word = Vocabulary.query.get(word_id)
    if not word:
        return jsonify({'success': False, 'message': '单词不存在'}), 404
    
    return jsonify({'success': True, 'data': word.to_dict()}), 200

@vocab_bp.route('/add', methods=['POST'])
@jwt_required()
def add_word():
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    data = request.get_json()
    word = Vocabulary(
        word=data['word'],
        meaning=data['meaning'],
        phonetic=data.get('phonetic', ''),
        example=data.get('example', ''),
        level=data.get('level', 2),
        frequency=data.get('frequency', 1),
        difficulty=data.get('difficulty', 1)
    )
    db.session.add(word)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '添加成功', 'data': word.to_dict()}), 201

@vocab_bp.route('/<int:word_id>', methods=['PUT'])
@jwt_required()
def update_word(word_id):
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    word = Vocabulary.query.get(word_id)
    if not word:
        return jsonify({'success': False, 'message': '单词不存在'}), 404
    
    data = request.get_json()
    if 'word' in data:
        word.word = data['word']
    if 'meaning' in data:
        word.meaning = data['meaning']
    if 'phonetic' in data:
        word.phonetic = data['phonetic']
    if 'example' in data:
        word.example = data['example']
    if 'level' in data:
        word.level = data['level']
    if 'frequency' in data:
        word.frequency = data['frequency']
    if 'difficulty' in data:
        word.difficulty = data['difficulty']
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': '更新成功', 'data': word.to_dict()}), 200

@vocab_bp.route('/<int:word_id>', methods=['DELETE'])
@jwt_required()
def delete_word(word_id):
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    word = Vocabulary.query.get(word_id)
    if not word:
        return jsonify({'success': False, 'message': '单词不存在'}), 404
    
    db.session.delete(word)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '删除成功'}), 200

@vocab_bp.route('/import', methods=['POST'])
@jwt_required()
def import_words():
    identity = get_jwt_identity()
    if identity.get('type') != 'admin':
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    
    data = request.get_json()
    words = data.get('words', [])
    success_count = 0
    fail_count = 0
    
    for item in words:
        try:
            word = Vocabulary(
                word=item['word'],
                meaning=item['meaning'],
                phonetic=item.get('phonetic', ''),
                example=item.get('example', ''),
                level=item.get('level', 2),
                frequency=item.get('frequency', 1),
                difficulty=item.get('difficulty', 1)
            )
            db.session.add(word)
            success_count += 1
        except Exception as e:
            fail_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'导入完成，成功 {success_count} 条，失败 {fail_count} 条'
    }), 200

@vocab_bp.route('/upload', methods=['POST'])
def upload_words():
    auth_header = request.headers.get('Authorization', '')
    print(f"Upload request - Auth header: {auth_header[:50] if auth_header else 'None'}...")
    
    if not auth_header.startswith('Bearer '):
        print("Upload failed: No Bearer token")
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    token = auth_header.split(' ')[1]
    try:
        import jwt
        from config.config import Config
        decoded = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
        print(f"Decoded token: {decoded}")
        
        sub = decoded.get('sub', {})
        if isinstance(sub, str):
            try:
                import json
                sub = json.loads(sub)
            except:
                pass
        
        if not isinstance(sub, dict) or sub.get('type') != 'admin':
            print(f"Upload failed: Not admin, sub={sub}")
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
    except Exception as e:
        print(f"Upload failed: Exception {e}")
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名为空'}), 400
    
    filename = file.filename.lower()
    if not (filename.endswith('.csv') or filename.endswith('.txt')):
        return jsonify({'success': False, 'message': '只支持 CSV 或 TXT 文件'}), 400
    
    try:
        content = file.read().decode('utf-8')
        success_count = 0
        fail_count = 0
        duplicates = 0
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) < 2:
                parts = line.split('\t')
            
            if len(parts) < 2:
                fail_count += 1
                continue
            
            word_text = parts[0].strip()
            meaning_text = parts[1].strip()
            
            if not word_text or not meaning_text:
                fail_count += 1
                continue
            
            existing = Vocabulary.query.filter_by(word=word_text).first()
            if existing:
                duplicates += 1
                continue
            
            level = 2
            frequency = 1
            difficulty = 1
            phonetic = ''
            example = ''
            
            if len(parts) >= 3:
                try:
                    level = int(parts[2].strip())
                except:
                    pass
            if len(parts) >= 4:
                try:
                    frequency = int(parts[3].strip())
                except:
                    pass
            if len(parts) >= 5:
                try:
                    difficulty = int(parts[4].strip())
                except:
                    pass
            if len(parts) >= 6:
                phonetic = parts[5].strip()
            if len(parts) >= 7:
                example = parts[6].strip()
            
            word = Vocabulary(
                word=word_text,
                meaning=meaning_text,
                phonetic=phonetic,
                example=example,
                level=level,
                frequency=frequency,
                difficulty=difficulty
            )
            db.session.add(word)
            success_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'上传完成！成功导入 {success_count} 条，重复跳过 {duplicates} 条，失败 {fail_count} 条'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'文件解析失败：{str(e)}'}), 400