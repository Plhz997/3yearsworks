"""
词汇文件智能解析器
支持多种格式自动识别并转换成系统统一格式
"""

import re
import csv
import io


def detect_and_parse(text):
    """
    智能检测文本格式并解析为词库条目列表

    逐行尝试多种分隔符，找到能拆分出 word + meaning 的方式即采用

    返回: list of dict
    """
    # 去除 UTF-8 BOM
    has_bom = text and text[0] == '\ufeff'
    if has_bom:
        text = text[1:]

    # 按行拆分
    raw_lines = text.strip().split('\n')
    lines = [l.strip() for l in raw_lines if l.strip()]
    
    if not lines:
        return []

    # 检测是否为CSV格式（60%的行有逗号）
    if _is_csv_format(lines):
        return _parse_csv(text)

    # 逐行解析，每行独立尝试不同分隔符
    result = []
    for line in lines:
        parsed = _parse_line_robust(line)
        if parsed:
            result.append(parsed)
    
    return result


def _is_csv_format(lines):
    """检测是否为CSV格式"""
    sample = lines[:5]
    csv_lines = 0
    for line in sample:
        if ',' in line:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 2:
                csv_lines += 1
    return csv_lines >= max(1, len(sample) * 0.6)


def _parse_csv(text):
    """解析CSV格式"""
    # 去除 BOM
    if text and text[0] == '\ufeff':
        text = text[1:]

    result = []
    reader = csv.reader(io.StringIO(text))
    headers = None
    
    for row in reader:
        if not row or all(cell.strip() == '' for cell in row):
            continue
        
        # 检测表头
        if headers is None and _is_header_row(row):
            headers = _normalize_headers(row)
            continue
        
        if headers:
            row_dict = dict(zip(headers, [r.strip() for r in row] + [''] * (len(headers) - len(row))))
        else:
            row_dict = _positional_map(row)
        
        word = row_dict.get('word', '').strip()
        meaning = row_dict.get('meaning', '').strip()
        
        if word and meaning:
            result.append(_build_entry(word, meaning, 
                          row_dict.get('phonetic', ''), 
                          row_dict.get('example', '')))
    
    return result


def _is_header_row(row):
    """判断是否为表头行"""
    header_keywords = ['word', '单词', '词汇', '英文', 'english', 'eng',
                       'meaning', '释义', '中文', '意思', 'chinese', 'chn',
                       'phonetic', '音标', '发音', 'example', '例句']
    for cell in row:
        if cell.strip().lower() in header_keywords:
            return True
    return False


def _normalize_headers(headers):
    """标准化表头名称"""
    mapping = {
        'word': 'word', '单词': 'word', '词汇': 'word', '英文': 'word',
        'english': 'word', 'eng': 'word',
        'meaning': 'meaning', '释义': 'meaning', '中文': 'meaning',
        '意思': 'meaning', 'chinese': 'meaning', 'chn': 'meaning',
        'phonetic': 'phonetic', '音标': 'phonetic', '发音': 'phonetic',
        'example': 'example', '例句': 'example',
    }
    return [mapping.get(h.strip().lower(), h.strip().lower()) for h in headers]


def _positional_map(row):
    """无表头时按位置映射"""
    clean = [r.strip() for r in row]
    return {
        'word': clean[0] if len(clean) > 0 else '',
        'meaning': clean[1] if len(clean) > 1 else '',
        'phonetic': clean[2] if len(clean) > 2 else '',
        'example': clean[3] if len(clean) > 3 else '',
    }


def _parse_line_robust(line):
    """逐行解析：依次尝试多种分隔符，找到能拆出 word+meaning 的方式"""
    # 去除行首编号
    line = re.sub(r'^[\s]*\d+[\.\)）]\s*', '', line)
    # 去除 Markdown 列表标记
    line = re.sub(r'^[\s]*[-*+]\s+', '', line)
    
    # 提取音标 /xxx/
    phonetic = ''
    phonetic_match = re.search(r'/([^/]+)/', line)
    if phonetic_match:
        phonetic = f"/{phonetic_match.group(1)}/"
        line = line.replace(phonetic_match.group(0), '').strip()
    
    # 依次尝试多种分隔符
    splitters = [
        ('\t', False),           # Tab
        (' - ', False),          # 中划线
        ('：', False),           # 中文冒号
        (':', True),             # 英文冒号（要求英文单词）
        ('  ', False),           # 双空格
        (' ', True),             # 单空格（要求英文单词）
    ]
    
    for sep, require_english in splitters:
        if sep in line:
            idx = line.index(sep)
            word = line[:idx].strip()
            meaning = line[idx + len(sep):].strip()
            
            # 如果要求英文单词，检查 word 是否看起来像英文
            if require_english and not _looks_like_english(word):
                continue
            
            # 要求 word 和 meaning 都有内容
            if not word or not meaning:
                continue
            
            # 要求 word 看起来像单词（至少包含字母）
            if not re.search(r'[a-zA-Z]', word):
                continue
            
            # 清理 word
            word = re.sub(r'[,.!?;:]+$', '', word)
            
            return _build_entry(word, meaning, phonetic, '')
    
    return None


def _looks_like_english(text):
    """判断文本是否像英文单词"""
    # 包含英文字母，且不是纯数字/符号
    return bool(re.match(r'^[a-zA-Z\'\-]+$', text) or 
                (re.search(r'[a-zA-Z]', text) and len(text) > 0))


def _build_entry(word, meaning, phonetic='', example=''):
    """构建标准词库条目"""
    # 分离meaning和example
    ex = ''
    example_match = re.search(r'[\(（]([^()（）]*?例句[：:][^()（）]*?)[\)）]', meaning)
    if example_match:
        ex = example_match.group(1)
        meaning = meaning.replace(example_match.group(0), '').strip()
    
    if example:
        ex = example or ex  # 从CSV column来
    
    return {
        'word': word.strip(),
        'meaning': meaning.strip(),
        'phonetic': phonetic.strip(),
        'example': ex.strip(),
        'level': _infer_level(word, meaning),
        'frequency': 1,
        'difficulty': 1
    }


def _infer_level(word, meaning):
    """根据单词长度和含义推断学段"""
    word_len = len(word.strip())
    
    elementary_keywords = ['你好', '苹果', '猫', '狗', '书', '颜色', '数字',
                           'hello', 'apple', 'cat', 'dog', 'book', 'color',
                           'red', 'blue', 'one', 'two', 'day', 'sun', 'big']
    for kw in elementary_keywords:
        if kw in word.lower() or kw in meaning:
            return 1
    
    if word_len >= 8:
        return 3
    
    advanced_keywords = ['哲学', '经济', '科学', '政治', '文化', '抽象',
                         'philosophy', 'economy', 'science', 'politics', 'abstract']
    for kw in advanced_keywords:
        if kw in meaning:
            return 3
    
    return 2