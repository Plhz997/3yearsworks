from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import jwt as pyjwt
import os
from config.config import Config
from models.vocabulary import Vocabulary
from models.favorite import Favorite
from models.wrong_word import WrongWord
from app import db
from utils.vocab_parser import detect_and_parse

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


def _require_admin():
    """验证管理员权限（手动解析JWT，因为 sub 是 dict 类型）"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    try:
        decoded = pyjwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'], options={"verify_sub": False})
        sub = decoded.get('sub')
        if isinstance(sub, dict) and sub.get('type') == 'admin':
            return sub
        return None
    except Exception:
        return None


@vocab_bp.route('/upload', methods=['POST'])
def upload_file():
    """上传词库文件并智能解析"""
    if not _require_admin():
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'}), 400

    allowed_extensions = {'.txt', '.csv', '.tsv'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        return jsonify({'success': False, 'message': f'不支持的文件格式: {ext}，请上传 {", ".join(allowed_extensions)} 文件'}), 400

    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            file.seek(0)
            content = file.read().decode('gbk')
        except UnicodeDecodeError:
            return jsonify({'success': False, 'message': '无法识别文件编码，请使用UTF-8或GBK编码'}), 400

    # 解析
    parsed = detect_and_parse(content)

    if not parsed:
        return jsonify({'success': False, 'message': '未能从文件中识别出单词，请检查格式'}), 400

    # 检查重复
    existing_words = {w.word.lower(): w.word for w in Vocabulary.query.all()}
    for pw in parsed:
        pw['duplicate'] = pw['word'].lower() in existing_words

    new_count = sum(1 for p in parsed if not p['duplicate'])
    dup_count = sum(1 for p in parsed if p['duplicate'])

    detected_format = 'CSV' if ext == '.csv' else (
        'TSV' if ext == '.tsv' else
        '空格分隔' if any(' ' in line for line in content.split('\n')[:3]) else
        '纯文本'
    )

    return jsonify({
        'success': True,
        'message': f'解析完成：共识别 {len(parsed)} 个单词（新增 {new_count} 个，重复 {dup_count} 个）',
        'data': parsed,
        'total': len(parsed),
        'new_count': new_count,
        'duplicate_count': dup_count,
        'detected_format': detected_format
    }), 200


@vocab_bp.route('/import-parsed', methods=['POST'])
def import_parsed():
    """确认导入解析后的单词"""
    if not _require_admin():
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403

    data = request.get_json()
    words = data.get('words', [])

    if not words:
        return jsonify({'success': False, 'message': '没有要导入的单词'}), 400

    success_count = 0
    skip_count = 0

    existing_words = {w.word.lower() for w in Vocabulary.query.all()}

    for item in words:
        if item.get('duplicate'):
            skip_count += 1
            continue

        word_lower = item['word'].strip().lower()
        if word_lower in existing_words:
            skip_count += 1
            continue

        try:
            vocab = Vocabulary(
                word=item['word'].strip(),
                meaning=item['meaning'].strip(),
                phonetic=item.get('phonetic', '').strip(),
                example=item.get('example', '').strip(),
                level=int(item.get('level', 2)),
                frequency=int(item.get('frequency', 1)),
                difficulty=int(item.get('difficulty', 1))
            )
            db.session.add(vocab)
            existing_words.add(word_lower)
            success_count += 1
        except Exception:
            skip_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'导入完成：成功 {success_count} 条，跳过 {skip_count} 条'
    }), 200


@vocab_bp.route('/batch-delete', methods=['POST'])
def batch_delete():
    """批量删除词库条目"""
    if not _require_admin():
        return jsonify({'success': False, 'message': '需要管理员权限'}), 403

    data = request.get_json()
    ids = data.get('ids', [])

    if not ids:
        return jsonify({'success': False, 'message': '请选择要删除的单词'}), 400

    try:
        ids = [int(i) for i in ids]
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': '无效的ID列表'}), 400

    count = Vocabulary.query.filter(Vocabulary.id.in_(ids)).delete(synchronize_session=False)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'成功删除 {count} 条'
    }), 200
