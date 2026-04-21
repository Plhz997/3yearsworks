import random
from sqlalchemy import func
from models.vocabulary import Vocabulary

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
        words = self.db.query(Vocabulary).filter_by(level=level).order_by(func.random()).limit(limit).all()
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
            question_type = random.choice(['choice_en', 'choice_zh', 'spelling', 'recognition'])
        
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
            options = self._generate_options(word, 'en')
            question['options'] = options
            
        elif question_type == 'choice_zh':
            question['prompt'] = f"请选择 '{word['word']}' 的中文释义"
            options = self._generate_options(word, 'zh')
            question['options'] = options
            
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
        is_correct = False
        
        if question['question_type'] == 'choice_en' or question['question_type'] == 'choice_zh':
            for option in question['options']:
                if option['key'] == user_answer and option.get('correct', False):
                    is_correct = True
                    break
                    
        elif question['question_type'] == 'spelling':
            is_correct = user_answer.strip().lower() == question['word'].lower()
            
        elif question['question_type'] == 'recognition':
            is_correct = user_answer == 'yes'
            
        return is_correct
    
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
        if not results:
            return 1
        
        total_score = 0
        level_weights = {1: 1.0, 2: 1.5, 3: 2.0}
        
        for result in results:
            weight = level_weights.get(result.get('level', 2), 1.5)
            if result['is_correct']:
                total_score += weight
        
        avg_score = total_score / len(results)
        
        if avg_score >= 1.8:
            return 3
        elif avg_score >= 1.2:
            return 2
        else:
            return 1
    
    def analyze_results(self, results):
        level_stats = {1: {'correct': 0, 'total': 0}, 
                      2: {'correct': 0, 'total': 0}, 
                      3: {'correct': 0, 'total': 0}}
        
        for result in results:
            level = result.get('level', 2)
            level_stats[level]['total'] += 1
            if result['is_correct']:
                level_stats[level]['correct'] += 1
        
        analysis = {
            'overall': {
                'total': len(results),
                'correct': sum(r['is_correct'] for r in results),
                'accuracy': sum(r['is_correct'] for r in results) / len(results) if results else 0
            },
            'level_analysis': {}
        }
        
        for level, stats in level_stats.items():
            if stats['total'] > 0:
                analysis['level_analysis'][self.LEVEL_NAMES[level]] = {
                    'correct': stats['correct'],
                    'total': stats['total'],
                    'accuracy': stats['correct'] / stats['total']
                }
        
        return analysis

class StandardTestAlgorithm(TestAlgorithm):
    """
    标准测评算法 - 按照指定规则出题
    """
    
    LEVEL_VOCAB_BASE = {
        (1, 1): 400,   # 小学1级
        (1, 2): 600,   # 小学2级
        (1, 3): 800,   # 小学3级
        (2, 1): 1000,  # 初中1级
        (2, 2): 1500,  # 初中2级
        (2, 3): 2000,  # 初中3级
        (3, 1): 2500,  # 高中1级
        (3, 2): 3500,  # 高中2级
        (3, 3): 4500   # 高中3级
    }
    
    LEVEL_WEIGHTS = {
        1: 1.25,
        2: 1.1,
        3: 1.1
    }
    
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
        order = [
            (1, 1), (1, 2), (1, 3),
            (2, 1), (2, 2), (2, 3),
            (3, 1), (3, 2), (3, 3)
        ]
        
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
        level_stats = {}
        for (level, diff), _ in self.TEST_DISTRIBUTION.items():
            level_stats[(level, diff)] = {'correct': 0, 'total': 0}
        
        for result in results:
            level = result.get('level', 2)
            diff = result.get('difficulty_level', 1)
            if (level, diff) in level_stats:
                level_stats[(level, diff)]['total'] += 1
                if result['is_correct']:
                    level_stats[(level, diff)]['correct'] += 1
        
        total_vocab = 0
        for (level, diff), stats in level_stats.items():
            if stats['total'] > 0:
                mastery_rate = stats['correct'] / stats['total']
                base_vocab = self.LEVEL_VOCAB_BASE.get((level, diff), 500)
                weight = self.LEVEL_WEIGHTS.get(level, 1.0)
                total_vocab += base_vocab * mastery_rate * weight
        
        return int(total_vocab)
    
    def evaluate_level(self, correct_count):
        if correct_count <= 10:
            return {'level': '入门级', 'description': '需要加强基础词汇学习'}
        elif correct_count <= 20:
            return {'level': '小学水平', 'description': '达到小学词汇水平'}
        elif correct_count <= 30:
            return {'level': '初中水平', 'description': '达到初中词汇水平'}
        elif correct_count <= 40:
            return {'level': '高中水平', 'description': '达到高中词汇水平'}
        else:
            return {'level': '优秀水平', 'description': '词汇水平优秀'}


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