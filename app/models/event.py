from datetime import datetime, timezone

from app import db


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(40), nullable=False, default="Other")
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(160), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False, default=100)
    registration_deadline = db.Column(db.Date, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    organizer = db.relationship("User", foreign_keys=[created_by])
    registrations = db.relationship("Registration", back_populates="event", cascade="all, delete-orphan")

    @property
    def status(self):
        today = datetime.now(timezone.utc).date()
        if self.event_date < today:
            return "Completed"
        if self.event_date == today:
            return "Ongoing"
        return "Upcoming"

    @property
    def participant_count(self):
        return sum(reg.status == "ACTIVE" for reg in self.registrations)
