from datetime import datetime, timezone

from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey("registrations.id"), unique=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    attendance_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = db.Column(db.String(20), default="PRESENT", nullable=False)
    marked_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    registration = db.relationship("Registration", back_populates="attendance")
    event = db.relationship("Event")
    student = db.relationship("User", foreign_keys=[user_id])
    marker = db.relationship("User", foreign_keys=[marked_by])
