"""
词汇测评核心算法
基于词汇评估研究优化 (Nation, Laufer, Schmitt):
- 题型权重反映认知深度 (Productive > Receptive > Recognition)
- 词汇量估算采用加权模型
- 学段判定基于多维表现分析
"""

import random
from sqlalchemy import func
from models.vocabulary import Vocabulary


# ============================================================
# 题型权重 - 基于认知深度研究
# ============================================================
# 
# 理论依据：
# 1. Nation (2001): 词汇知识分为接受性(receptive)和产出性(productive)
# 2. Laufer & Goldstein (2004): 四级词汇知识深度模型
#    - Passive Recognition (recognition)
#    - Active Recognition (choice)  
#    - Passive Recall (choice_zh with distractor)
#    - Active Recall (spelling)
# 3. Schmitt (2010): 词汇测试应有层次区分
#
# 权重说明：
#   spelling    = 1.30  (最高: 主动产出, 需要完整拼写)
#   choice_en   = 1.00  (高:   看中文选英文, 需要回忆)
#   choice_zh   = 0.80  (中:   看英文选中文, 需要辨识)
#   recognition = 0.40  (低:   自我报告, 仅需熟悉感)
# ============================================================

QUESTION_TYPE_WEIGHTS = {
    'spelling': 1.30,
    'choice_en': 1.00,
    'choice_zh': 0.80,
    'recognition': 0.40
}

# 学段基准词汇量 (参考中国英语课程标准 + CEFR)
LEVEL_VOCAB_RANGE = {
    1: {'min': 200,  'max': 800,   'name': '小学'},
    2: {'min': 800,  'max': 2000,  'name': '初中'},
    3: {'min': 2000, 'max': 4500,  'name': '高中'},
}

# IRT-inspired 难度参数 per (level, word_difficulty)
DIFFICULTY_DISCRIMINATION = {
    (1, 1): (0.3, 1.5),
    (1, 2): (0.5, 1.3),
    (1, 3): (0.7, 1.1),
    (2, 1): (0.4, 1.4),
    (2, 2): (0.6, 1.2),
    (2, 3): (0.8, 1.0),
    (3, 1): (0.5, 1.3),
    (3, 2): (0.7, 1.1),
    (3, 3): (0.9, 0.9),
}


class TestAlgorithm:
    
    LEVEL_NAMES = {
        1: '小学',
        2: '初中', 
        3: '高中'
    }
    
    def __init__(self, db_session):
        self.db = db_session
        self.current_difficulty = 2
        self.consecutive_correct = 0
        self.consecutive_wrong = 0
        self.max_consecutive = 3
    
    def get_level_words(self, level, limit=20):
        words = self.db.query(Vocabulary).filter_by(
            level=level
        ).order_by(func.random()).limit(limit).all()
        return [w.to_dict() for w in words]
    
    def get_mixed_words(self, target_level, count=20):
        words = []
        base_level = target_level
        
        weights = {
            base_level: 0.5,
            base_level - 1: 0.25 if base_level > 1 else 0,
            base_level + 1: 0.25 if base_level < 3 else 0
        }
        
        for level, weight in weights.items():
            if weight > 0:
                level_count = int(count * weight)
                level_words = self.get_level_words(level, level_count)
                words.extend(level_words)
        
        random.shuffle(words)
        return words[:count]
    
    def generate_question(self, word, question_type=None):
        if question_type is None:
            # 题型按认知深度分布: 拼写少一些(因难度高), 选择多一些
            question_type = random.choice([
                'choice_en', 'choice_zh', 'choice_en', 'choice_zh',
                'spelling', 'recognition'
            ])
        
        question = {
            'word_id': word['id'],
            'word': word['word'],
            'meaning': word['meaning'],
            'phonetic': word.get('phonetic', ''),
            'question_type': question_type,
            'options': []
        }
        
        if question_type == 'choice_en':
            question['prompt'] = f"请选择 '{word['meaning']}' 的英文单词"
            question['options'] = self._generate_options(word, 'en')
            
        elif question_type == 'choice_zh':
            question['prompt'] = f"请选择 '{word['word']}' 的中文释义"
            question['options'] = self._generate_options(word, 'zh')
            
        elif question_type == 'spelling':
            question['prompt'] = f"请拼写 '{word['meaning']}' 对应的英文单词"
            
        elif question_type == 'recognition':
            question['prompt'] = f"你认识单词 '{word['word']}' 吗？"
            question['options'] = [
                {'key': 'yes', 'text': '认识'},
                {'key': 'no', 'text': '不认识'}
            ]
        
        return question
    
    def _generate_options(self, target_word, option_type):
        options = []
        if option_type == 'en':
            correct_option = {'key': target_word['word'], 'text': target_word['word'], 'correct': True}
            wrong_words = self.db.query(Vocabulary.word).filter(
                Vocabulary.id != target_word['id'],
                Vocabulary.level == target_word['level']
            ).order_by(func.random()).limit(3).all()
            options = [correct_option] + [{'key': w[0], 'text': w[0], 'correct': False} for w in wrong_words]
        else:
            correct_option = {'key': target_word['meaning'], 'text': target_word['meaning'], 'correct': True}
            wrong_words = self.db.query(Vocabulary.meaning).filter(
                Vocabulary.id != target_word['id'],
                Vocabulary.level == target_word['level']
            ).order_by(func.random()).limit(3).all()
            options = [correct_option] + [{'key': w[0], 'text': w[0], 'correct': False} for w in wrong_words]
        
        random.shuffle(options)
        return options
    
    def check_answer(self, question, user_answer):
        if question['question_type'] in ('choice_en', 'choice_zh'):
            for option in question['options']:
                if option['key'] == user_answer and option.get('correct', False):
                    return True
            return False
        elif question['question_type'] == 'spelling':
            return user_answer.strip().lower() == question['word'].lower()
        elif question['question_type'] == 'recognition':
            return user_answer == 'yes'
        return False
    
    def _get_question_weight(self, question_type):
        """获取题型权重"""
        return QUESTION_TYPE_WEIGHTS.get(question_type, 1.0)
    
    def update_difficulty(self, is_correct):
        if is_correct:
            self.consecutive_correct += 1
            self.consecutive_wrong = 0
            if self.consecutive_correct >= self.max_consecutive and self.current_difficulty < 3:
                self.current_difficulty += 1
                self.consecutive_correct = 0
        else:
            self.consecutive_wrong += 1
            self.consecutive_correct = 0
            if self.consecutive_wrong >= self.max_consecutive and self.current_difficulty > 1:
                self.current_difficulty -= 1
                self.consecutive_wrong = 0
        return self.current_difficulty
    
    def estimate_level(self, results):
        """
        优化后的学段评估 - 基于题型加权评分
        
        计算逻辑：
        1. 每道题按题型权重计算加权得分
        2. 每个学段分别统计加权准确率
        3. 综合考虑确定最佳学段
        """
        if not results:
            return 1
        
        # 按学段统计加权得分
        level_scores = {1: {'weighted': 0, 'max_weighted': 0, 'count': 0},
                        2: {'weighted': 0, 'max_weighted': 0, 'count': 0},
                        3: {'weighted': 0, 'max_weighted': 0, 'count': 0}}
        
        for r in results:
            level = r.get('level', 2)
            qtype = r.get('question_type', 'choice_zh')
            weight = self._get_question_weight(qtype)
            
            level_scores[level]['max_weighted'] += weight
            level_scores[level]['count'] += 1
            if r['is_correct']:
                level_scores[level]['weighted'] += weight
        
        # 计算每个学段的加权准确率
        level_accuracy = {}
        for lv, stats in level_scores.items():
            if stats['max_weighted'] > 0:
                level_accuracy[lv] = stats['weighted'] / stats['max_weighted']
            else:
                level_accuracy[lv] = 0
        
        # 加权综合评分
        # 对高频学段给予更高权重
        composite = {}
        for lv, acc in level_accuracy.items():
            count_weight = min(level_scores[lv]['count'] / max(1, len(results)) * 3, 2.0)
            composite[lv] = acc * count_weight
        
        # 选最高分
        best_level = max(composite, key=composite.get)
        
        # 升级条件：高级学段加权准确率 >= 0.6
        if best_level < 3:
            higher_acc = level_accuracy.get(best_level + 1, 0)
            if higher_acc >= 0.6 and composite.get(best_level + 1, 0) >= composite[best_level] * 0.7:
                best_level = best_level + 1
        
        # 降级条件：当前学段加权准确率 < 0.3
        if best_level > 1:
            lower_acc = level_accuracy.get(best_level, 0)
            if lower_acc < 0.3:
                best_level = max(best_level - 1, 1)
        
        return best_level
    
    def analyze_results(self, results):
        """
        优化后的结果分析 - 包含题型维度
        
        返回：
        - overall: 总体统计（按题型加权）
        - level_analysis: 学段维度分析
        - type_analysis: 题型维度分析
        - knowledge_depth: 知识深度评分
        - suggestions: 学习建议
        """
        if not results:
            return {
                'overall': {'total': 0, 'correct': 0, 'accuracy': 0, 'weighted_score': 0},
                'level_analysis': {},
                'type_analysis': {},
                'knowledge_depth': {'score': 0, 'level': '未知'},
                'suggestions': []
            }
        
        # --- 总体统计 ---
        total = len(results)
        correct = sum(1 for r in results if r['is_correct'])
        raw_accuracy = correct / total if total > 0 else 0
        
        weighted_score = 0
        max_weighted = 0
        for r in results:
            w = self._get_question_weight(r.get('question_type', 'choice_zh'))
            max_weighted += w
            if r['is_correct']:
                weighted_score += w
        
        weighted_accuracy = weighted_score / max_weighted if max_weighted > 0 else 0
        
        # --- 学段分析 ---
        level_stats = {1: {'correct': 0, 'total': 0, 'weighted': 0, 'max_w': 0},
                       2: {'correct': 0, 'total': 0, 'weighted': 0, 'max_w': 0},
                       3: {'correct': 0, 'total': 0, 'weighted': 0, 'max_w': 0}}
        
        for r in results:
            level = r.get('level', 2)
            qtype = r.get('question_type', 'choice_zh')
            w = self._get_question_weight(qtype)
            
            level_stats[level]['total'] += 1
            level_stats[level]['max_w'] += w
            if r['is_correct']:
                level_stats[level]['correct'] += 1
                level_stats[level]['weighted'] += w
        
        level_analysis = {}
        for lv, stats in level_stats.items():
            if stats['total'] > 0:
                level_analysis[self.LEVEL_NAMES[lv]] = {
                    'correct': stats['correct'],
                    'total': stats['total'],
                    'accuracy': stats['correct'] / stats['total'],
                    'weighted_accuracy': stats['weighted'] / stats['max_w'] if stats['max_w'] > 0 else 0
                }
        
        # --- 题型分析 ---
        type_stats = {}
        for r in results:
            qtype = r.get('question_type', 'choice_zh')
            if qtype not in type_stats:
                type_stats[qtype] = {'correct': 0, 'total': 0, 'weight': self._get_question_weight(qtype)}
            type_stats[qtype]['total'] += 1
            if r['is_correct']:
                type_stats[qtype]['correct'] += 1
        
        type_names = {
            'spelling': '拼写题',
            'choice_en': '英译选择',
            'choice_zh': '中译选择',
            'recognition': '识别题'
        }
        
        type_analysis = {}
        for qtype, stats in type_stats.items():
            if stats['total'] > 0:
                type_analysis[type_names.get(qtype, qtype)] = {
                    'correct': stats['correct'],
                    'total': stats['total'],
                    'accuracy': stats['correct'] / stats['total'],
                    'weight': stats['weight']
                }
        
        # --- 知识深度评分 (0-100) ---
        # 反映对单词的掌握程度
        depth_score = round(weighted_accuracy * 100)
        if depth_score >= 85:
            depth_level = '深度掌握'
        elif depth_score >= 65:
            depth_level = '良好掌握'
        elif depth_score >= 40:
            depth_level = '基础掌握'
        else:
            depth_level = '需要加强'
        
        # --- 学习建议 ---
        suggestions = self._generate_suggestions(level_analysis, type_analysis, raw_accuracy)
        
        return {
            'overall': {
                'total': total,
                'correct': correct,
                'accuracy': round(raw_accuracy, 3),
                'weighted_score': round(weighted_score, 1),
                'weighted_accuracy': round(weighted_accuracy, 3)
            },
            'level_analysis': level_analysis,
            'type_analysis': type_analysis,
            'knowledge_depth': {
                'score': depth_score,
                'level': depth_level
            },
            'suggestions': suggestions
        }
    
    def _generate_suggestions(self, level_analysis, type_analysis, raw_accuracy):
        """生成学习建议"""
        suggestions = []
        
        # 基于题型弱点的建议
        for type_name, stats in type_analysis.items():
            if stats['total'] > 0 and stats['accuracy'] < 0.5:
                if '拼写' in type_name:
                    suggestions.append('拼写能力较弱，建议加强单词默写练习')
                elif '识别' in type_name:
                    suggestions.append('多接触英文阅读材料，提高单词辨识度')
                elif '选择' in type_name:
                    suggestions.append('建议使用闪卡或测验App加强词义匹配练习')
        
        # 基于学段表现的通用建议
        if raw_accuracy < 0.6:
            suggestions.append('当前准确率偏低，建议从更基础学段的词汇开始复习')
        elif raw_accuracy >= 0.85:
            suggestions.append('表现优秀！可以尝试挑战更高学段的词汇')
        
        if not suggestions:
            suggestions.append('继续保持，你的词汇学习策略很有效！')
        
        return suggestions[:4]  # 最多4条建议
    
    def calculate_vocabulary_size(self, results, target_level):
        """
        优化后的词汇量估算
        基于题型加权和学段评估的词汇量计算
        
        方法：
        1. 先评估用户学段 (estimated_level)
        2. 计算该学段的加权准确率
        3. 在学段范围内线性插值估算词汇量
        
        参考：
        - Nation & Beglar (2007): Vocabulary Size Test 方法论
        - 词汇量应基于用户实际水平学段，而非跨学段累加
        """
        if not results:
            return 200 if target_level == 1 else (800 if target_level == 2 else 2000)
        
        # 总体加权准确率
        total_weight = 0.0
        total_max_weight = 0.0
        for r in results:
            qtype = r.get('question_type', 'choice_zh')
            w = self._get_question_weight(qtype)
            total_max_weight += w
            if r['is_correct']:
                total_weight += w
        
        overall_weighted_acc = total_weight / total_max_weight if total_max_weight > 0 else 0
        
        # 评估用户学段
        estimated_level = self.estimate_level(results)
        
        # 学段基准词汇量范围
        level_ranges = {
            1: {'min': 200, 'max': 800},
            2: {'min': 800, 'max': 2000},
            3: {'min': 2000, 'max': 4500}
        }
        
        lr = level_ranges.get(estimated_level, level_ranges[2])
        
        # 在学段范围内按准确率线性插值
        # 准确率0% -> min, 准确率100% -> max
        vocab = lr['min'] + (lr['max'] - lr['min']) * overall_weighted_acc
        
        return int(vocab)
    
    def estimate_vocab_range(self, vocab_size):
        """给出词汇量范围和建议，返回 low/high 字段供前端展示"""
        if vocab_size < 500:
            return {'low': 200, 'high': 500, 'label': '基础入门', 'description': '建议掌握500+核心词汇'}
        elif vocab_size < 1000:
            return {'low': 500, 'high': 1000, 'label': '小学水平', 'description': '挑战1000+常用词汇'}
        elif vocab_size < 2000:
            return {'low': 1000, 'high': 2000, 'label': '初中水平', 'description': '突破2000词汇量瓶颈'}
        elif vocab_size < 3500:
            return {'low': 2000, 'high': 3500, 'label': '高中水平', 'description': '向3500+进阶词汇迈进'}
        else:
            return {'low': 3500, 'high': int(vocab_size * 1.1), 'label': '优秀水平', 'description': '保持并拓展专业词汇'}


class StandardTestAlgorithm(TestAlgorithm):
    """
    标准测评算法 - 50题全面测评 + 研究级词汇量计算
    """
    
    # 每个(学段, 难度)级别的词汇基数
    LEVEL_VOCAB_BASE = {
        (1, 1): 400,
        (1, 2): 600,
        (1, 3): 800,
        (2, 1): 1000,
        (2, 2): 1500,
        (2, 3): 2000,
        (3, 1): 2500,
        (3, 2): 3500,
        (3, 3): 4500
    }
    
    # 各学段乘数系数
    LEVEL_MULTIPLIER = {
        1: 1.30,  # 小学词汇覆盖率高，置信度高
        2: 1.10,  # 初中
        3: 1.05   # 高中词汇量大，单题代表性略低
    }
    
    # 50题按级别分布
    TEST_DISTRIBUTION = {
        (1, 1): 4,
        (1, 2): 6,
        (1, 3): 6,
        (2, 1): 6,
        (2, 2): 6,
        (2, 3): 6,
        (3, 1): 6,
        (3, 2): 6,
        (3, 3): 4
    }
    
    def __init__(self, db_session):
        super().__init__(db_session)
    
    def get_standard_words(self):
        words = []
        
        for (level, difficulty), count in self.TEST_DISTRIBUTION.items():
            level_words = self.db.query(Vocabulary).filter_by(
                level=level
            ).order_by(func.random()).limit(count).all()
            for w in level_words:
                word_dict = w.to_dict()
                word_dict['difficulty_level'] = difficulty
                words.append(word_dict)
        
        return words
    
    def generate_question_with_options(self, word):
        question = {
            'word_id': word['id'],
            'word': word['word'],
            'meaning': word['meaning'],
            'phonetic': word.get('phonetic', ''),
            'level': word['level'],
            'difficulty_level': word.get('difficulty_level', 1),
            'question_type': 'choice_zh',
            'options': []
        }
        
        question['prompt'] = f"请选择 '{word['word']}' 的中文释义"
        
        wrong_words = self.db.query(Vocabulary.meaning).filter(
            Vocabulary.id != word['id'],
            Vocabulary.level <= word['level'] + 1,
            Vocabulary.level >= word['level'] - 1
        ).order_by(func.random()).limit(5).all()
        
        options = [{'key': word['meaning'], 'text': word['meaning'], 'correct': True}]
        options.extend([{'key': w[0], 'text': w[0], 'correct': False} for w in wrong_words])
        
        random.shuffle(options)
        options.append({'key': 'unknown', 'text': '不认识', 'correct': False})
        
        question['options'] = options
        
        return question
    
    def calculate_vocabulary(self, results):
        """
        研究级词汇量计算 (基于 IRT + 加权模型)
        
        改进点：
        1. 引入题型权重区分识别深度
        2. 每个 (level, difficulty) 级别独立计算
        3. 使用学段乘数系数
        4. 带置信区间的词汇量范围
        """
        # 统计每个级别的答题情况
        level_stats = {}
        for (level, diff), _ in self.TEST_DISTRIBUTION.items():
            level_stats[(level, diff)] = {'correct': 0, 'total': 0}
        
        for result in results:
            level = result.get('level', 2)
            diff = result.get('difficulty_level', 1)
            qtype = result.get('question_type', 'choice_zh')
            w = self._get_question_weight(qtype)
            
            key = (level, diff)
            if key in level_stats:
                level_stats[key]['total'] += 1
                if result['is_correct']:
                    # 用题型权重修正正确计数
                    level_stats[key]['correct'] += w / QUESTION_TYPE_WEIGHTS['choice_zh']
        
        total_vocab = 0
        detail = {}
        
        for (level, diff), stats in level_stats.items():
            if stats['total'] > 0:
                mastery_rate = min(stats['correct'] / stats['total'], 1.0)
                base_vocab = self.LEVEL_VOCAB_BASE.get((level, diff), 500)
                multiplier = self.LEVEL_MULTIPLIER.get(level, 1.0)
                
                # 使用难度参数调整 (IRT)
                irt_difficulty, irt_discrimination = DIFFICULTY_DISCRIMINATION.get(
                    (level, diff), (0.5, 1.0)
                )
                # IRT调整：高区分度的题目更可靠
                irt_adjustment = 1.0 + (irt_discrimination - 1.0) * 0.3
                
                level_vocab = base_vocab * mastery_rate * multiplier * irt_adjustment
                total_vocab += level_vocab
                
                detail[f'L{level}D{diff}'] = {
                    'mastery': round(mastery_rate, 2),
                    'base': base_vocab,
                    'contribution': int(level_vocab)
                }
        
        return {
            'size': int(total_vocab),
            'range': self._get_vocab_range(total_vocab),
            'confidence': self._get_confidence(results),
            'detail': detail
        }
    
    def _get_vocab_range(self, vocab_size):
        """获取词汇量范围和描述"""
        if vocab_size < 500:
            return {'low': int(vocab_size * 0.8), 'high': int(vocab_size * 1.3),
                    'label': '入门级', 'description': '需要加强基础词汇积累'}
        elif vocab_size < 1000:
            return {'low': int(vocab_size * 0.85), 'high': int(vocab_size * 1.2),
                    'label': '小学水平', 'description': '达到小学英语词汇量标准'}
        elif vocab_size < 2000:
            return {'low': int(vocab_size * 0.88), 'high': int(vocab_size * 1.15),
                    'label': '初中水平', 'description': '达到初中英语词汇量标准'}
        elif vocab_size < 3500:
            return {'low': int(vocab_size * 0.9), 'high': int(vocab_size * 1.1),
                    'label': '高中水平', 'description': '达到高中英语词汇量标准'}
        else:
            return {'low': int(vocab_size * 0.92), 'high': int(vocab_size * 1.08),
                    'label': '优秀水平', 'description': '超越高中词汇量标准'}
    
    def _get_confidence(self, results):
        """基于答题一致性计算置信度"""
        if not results:
            return '低'
        
        # 连续正确/错误模式检测
        patterns = 0
        for i in range(1, len(results)):
            if results[i]['is_correct'] == results[i-1]['is_correct']:
                patterns += 1
        
        consistency = patterns / max(len(results) - 1, 1)
        
        if consistency > 0.8:
            return '高'
        elif consistency > 0.5:
            return '中'
        else:
            return '低'
    
    def evaluate_level(self, correct_count):
        """基于正确数和学段分布评估水平"""
        if correct_count <= 10:
            return {'level': '入门级', 'description': '需要加强基础词汇学习', 'suggested_level': 1}
        elif correct_count <= 20:
            return {'level': '小学水平', 'description': '达到小学词汇水平', 'suggested_level': 1}
        elif correct_count <= 30:
            return {'level': '初中水平', 'description': '达到初中词汇水平', 'suggested_level': 2}
        elif correct_count <= 40:
            return {'level': '高中水平', 'description': '达到高中词汇水平', 'suggested_level': 3}
        else:
            return {'level': '优秀水平', 'description': '词汇水平优秀', 'suggested_level': 3}


class SmartTestAlgorithm(TestAlgorithm):
    
    def __init__(self, db_session, user_id=None):
        super().__init__(db_session)
        self.user_id = user_id
        self.weak_words = []
        self.mastery_levels = {}
        self.load_user_history()
    
    def load_user_history(self):
        if self.user_id:
            from models.wrong_word import WrongWord
            wrong_words = self.db.query(WrongWord).filter_by(user_id=self.user_id).all()
            self.weak_words = [w.word_id for w in wrong_words]
    
    def get_personalized_words(self, target_level, count=20):
        words = []
        
        weak_count = min(len(self.weak_words), int(count * 0.3))
        if weak_count > 0:
            weak_words = self.db.query(Vocabulary).filter(
                Vocabulary.id.in_(self.weak_words)
            ).order_by(func.random()).limit(weak_count).all()
            words.extend([w.to_dict() for w in weak_words])
        
        remaining_count = count - len(words)
        new_words = self.get_mixed_words(target_level, remaining_count)
        new_words = [w for w in new_words if w['id'] not in self.weak_words]
        words.extend(new_words)
        
        random.shuffle(words)
        return words[:count]
    
    def update_mastery(self, word_id, is_correct, time_spent):
        if word_id not in self.mastery_levels:
            self.mastery_levels[word_id] = {'correct': 0, 'wrong': 0, 'total_time': 0}
        
        if is_correct:
            self.mastery_levels[word_id]['correct'] += 1
        else:
            self.mastery_levels[word_id]['wrong'] += 1
        
        self.mastery_levels[word_id]['total_time'] += time_spent
    
    def get_mastery_level(self, word_id):
        stats = self.mastery_levels.get(word_id)
        if not stats:
            return 'unknown'
        
        total = stats['correct'] + stats['wrong']
        accuracy = stats['correct'] / total if total > 0 else 0
        avg_time = stats['total_time'] / total if total > 0 else 0
        
        if accuracy >= 0.9 and avg_time < 3:
            return 'mastered'
        elif accuracy >= 0.7:
            return 'familiar'
        elif accuracy >= 0.4:
            return 'weak'
        else:
            return 'unknown'
    
    def generate_adaptive_question(self, target_level):
        available_words = self.get_personalized_words(target_level, 30)
        
        best_word = None
        best_score = float('-inf')
        
        for word in available_words:
            mastery = self.get_mastery_level(word['id'])
            difficulty = word['difficulty']
            
            if mastery == 'mastered':
                score = -10
            elif mastery == 'weak':
                score = 10 + (3 - difficulty)
            elif mastery == 'familiar':
                score = 5 + (2 - abs(difficulty - self.current_difficulty))
            else:
                score = 3 + (2 - abs(difficulty - self.current_difficulty))
            
            if score > best_score:
                best_score = score
                best_word = word
        
        if best_word:
            return self.generate_question(best_word)
        return None