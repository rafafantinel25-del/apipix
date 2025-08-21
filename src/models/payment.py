from uuid import uuid4
from datetime import datetime, timedelta
from .base import db, TimestampMixin

class Payment(db.Model, TimestampMixin):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_id = db.Column(db.String(64), unique=True, index=True)
    user_id = db.Column(db.String(64), nullable=False, index=True)
    plan_type = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(16), default='pending', index=True)
    pix_code = db.Column(db.Text)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(minutes=30))
    paid_at = db.Column(db.DateTime)

