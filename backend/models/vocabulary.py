from app import db

class Vocabulary(db.Model):
    __tablename__ = 'vocabulary'
    
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    phonetic = db.Column(db.String(50))
    example = db.Column(db.Text)
    level = db.Column(db.Integer, nullable=False, default=1)
    frequency = db.Column(db.Integer, nullable=False, default=1)
    difficulty = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'meaning': self.meaning,
            'phonetic': self.phonetic,
            'example': self.example,
            'level': self.level,
            'frequency': self.frequency,
            'difficulty': self.difficulty,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }