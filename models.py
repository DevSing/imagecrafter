from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db  # ✅ Import from extensions, not circularly

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tools_used = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SiteStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitors = db.Column(db.Integer, default=0)
    files_converted = db.Column(db.Integer, default=0)
