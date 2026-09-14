import uuid
from datetime import datetime, timezone

from app import db


class Registration(db.Model):
    __tablename__ = "registrations"
    __table_args__ = (db.UniqueConstraint("user_id", "event_id", name="unique_event_registration"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    registration_code = db.Column(db.String(64), unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    qr_code = db.Column(db.String(255), nullable=True)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default="ACTIVE", nullable=False)
    user = db.relationship("User", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")
    attendance = db.relationship("Attendance", back_populates="registration", uselist=False, cascade="all, delete-orphan")
