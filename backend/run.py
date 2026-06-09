import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Admin, Vocabulary, TestRecord, TestDetail, WrongWord, Favorite, PomodoroRecord
from utils.sample_data import init_sample_data

app = create_app()

with app.app_context():
    db.create_all()
    
    if not Admin.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin = Admin(username='admin', password=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
    
    init_sample_data(db.session)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8081))
    app.run(host='0.0.0.0', port=port, debug=True)
