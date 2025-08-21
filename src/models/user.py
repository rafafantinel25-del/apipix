from .base import db, TimestampMixin

class User(db.Model, TimestampMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    telegram_user_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    name = db.Column(db.String(128))
    plan_type = db.Column(db.String(32))
    is_vip = db.Column(db.Boolean, default=False)

