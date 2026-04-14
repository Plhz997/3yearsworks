from app import db

class TestRecord(db.Model):
    __tablename__ = 'test_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    level = db.Column(db.Integer, nullable=False)
    total_count = db.Column(db.Integer, nullable=False)
    correct_count = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)
    estimated_level = db.Column(db.Integer)
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'level': self.level,
            'total_count': self.total_count,
            'correct_count': self.correct_count,
            'accuracy': self.accuracy,
            'duration': self.duration,
            'estimated_level': self.estimated_level,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }