from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
db.create_all()
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Registered user model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tools_used = db.Column(db.Integer, default=0)  # Tracks how many tools the user has used

    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the provided password."""
        return check_password_hash(self.password_hash, password)


class SiteStat(db.Model):
    """Tracks overall site usage (visitor + conversion stats)."""
    id = db.Column(db.Integer, primary_key=True)
    visitors = db.Column(db.Integer, default=0)          # Total site visitors
    files_converted = db.Column(db.Integer, default=0)   # Total converted/downloaded files

