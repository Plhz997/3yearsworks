from app import db

class PomodoroRecord(db.Model):
    __tablename__ = 'pomodoro_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    word_group = db.Column(db.String(50), nullable=False, default='level_2')
    task_type = db.Column(db.String(50), nullable=False, default='wrong')
    duration_seconds = db.Column(db.Integer, nullable=False, default=0)
    target_count = db.Column(db.Integer, nullable=False, default=0)
    completed_count = db.Column(db.Integer, nullable=False, default=0)
    correct_count = db.Column(db.Integer, nullable=False, default=0)
    accuracy = db.Column(db.Float, nullable=False, default=0)
    coffee_beans = db.Column(db.Integer, nullable=False, default=0)
    energy_value = db.Column(db.Integer, nullable=False, default=0)
    recommendation = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'word_group': self.word_group,
            'task_type': self.task_type,
            'duration_seconds': self.duration_seconds,
            'target_count': self.target_count,
            'completed_count': self.completed_count,
            'correct_count': self.correct_count,
            'accuracy': self.accuracy,
            'coffee_beans': self.coffee_beans,
            'energy_value': self.energy_value,
            'recommendation': self.recommendation,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
