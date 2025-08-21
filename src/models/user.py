from .base import db, TimestampMixin

class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # Telegram user id
    username = db.Column(db.String(64))
    first_name = db.Column(db.String(128))
    plan_type = db.Column(db.String(32))
    is_vip = db.Column(db.Boolean, default=False)

