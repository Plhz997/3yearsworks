from app import db

class WrongWord(db.Model):
    __tablename__ = 'wrong_words'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'), nullable=False)
    wrong_count = db.Column(db.Integer, nullable=False, default=1)
    last_wrong_time = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_id': self.word_id,
            'wrong_count': self.wrong_count,
            'last_wrong_time': self.last_wrong_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_wrong_time else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }