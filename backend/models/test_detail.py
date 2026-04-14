from app import db

class TestDetail(db.Model):
    __tablename__ = 'test_details'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('test_records.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Integer, nullable=False, default=0)
    time_spent = db.Column(db.Integer)
    question_type = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'record_id': self.record_id,
            'word_id': self.word_id,
            'word': self.word,
            'meaning': self.meaning,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'time_spent': self.time_spent,
            'question_type': self.question_type
        }