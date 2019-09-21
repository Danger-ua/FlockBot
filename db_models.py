from datetime import datetime, timedelta
from main import db
from crypto import get_random_token


class Credential(db.Model):
    id = db.Column(db.String(18), unique=True, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    plugin = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"user_id: {self.id}, name: {self.username}, pass: {self.password}"


class RegistrationUrl(db.Model):
    url = db.Column(db.String(10), unique=True, primary_key=True, default=get_random_token(5))
    user_id = db.Column(db.String(18), unique=True, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False, default=datetime.utcnow() + timedelta(minutes=5))

    def __init__(self, *args, **kwargs):
        super(RegistrationUrl, self).__init__(*args, **kwargs)
        self.url = get_random_token(5)
        self.expiration = datetime.utcnow() + timedelta(minutes=5)

    def __repr__(self):
        return f"url: {self.url}, user_id: {self.user_id}, expiration: {self.expiration}"

