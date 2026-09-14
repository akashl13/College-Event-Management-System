from app import db
from app.models import Attendance, Registration


def mark_registration_attendance(code, marker_id):
    registration = Registration.query.filter_by(registration_code=code, status="ACTIVE").first()
    if not registration:
        return None, "Registration is invalid or cancelled."
    if registration.attendance:
        return registration.attendance, "Attendance Already Recorded"
    attendance = Attendance(
        registration_id=registration.id,
        event_id=registration.event_id,
        user_id=registration.user_id,
        marked_by=marker_id,
    )
    db.session.add(attendance)
    db.session.commit()
    return attendance, "Attendance Successfully Marked"
