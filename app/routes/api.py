from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user

from app import db
from app.models import Attendance, Event, Registration, User
from app.services.attendance_service import mark_registration_attendance
from app.services.qr_service import create_registration_qr
from app.utils.decorators import roles_required

api_bp = Blueprint("api", __name__)

def event_json(event):
    return {"id": event.id, "title": event.title, "description": event.description, "category": event.category, "date": event.event_date.isoformat(), "time": event.start_time.strftime("%I:%M %p"), "end_time": event.end_time.strftime("%I:%M %p"), "venue": event.venue, "status": event.status, "participants": event.participant_count, "capacity": event.max_participants}

@api_bp.get("/events")
def list_events():
    return jsonify([event_json(event) for event in Event.query.order_by(Event.event_date).all()])

@api_bp.get("/events/<int:event_id>")
def get_event(event_id):
    return jsonify(event_json(Event.query.get_or_404(event_id)))

@api_bp.post("/auth/register")
def api_register():
    data = request.get_json() or {}
    if not data.get("email") or not data.get("password") or User.query.filter_by(email=data["email"].lower()).first():
        return jsonify({"error": "Valid, unique email and password are required."}), 400
    user = User(full_name=data.get("full_name", "Student"), email=data["email"].lower(), student_id=data.get("student_id"))
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "message": "Account created"}), 201

@api_bp.post("/auth/login")
def api_login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email", "").lower()).first()
    if not user or not user.check_password(data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401
    login_user(user)
    return jsonify({"id": user.id, "name": user.full_name, "role": user.role})

@api_bp.post("/registrations")
@login_required
def api_register_event():
    event = Event.query.get_or_404((request.get_json() or {}).get("event_id"))
    if Registration.query.filter_by(user_id=current_user.id, event_id=event.id).first():
        return jsonify({"error": "Already registered"}), 409
    registration = Registration(user_id=current_user.id, event_id=event.id)
    db.session.add(registration)
    db.session.flush()
    create_registration_qr(registration)
    db.session.commit()
    return jsonify({"id": registration.id, "registration_code": registration.registration_code, "qr_code": registration.qr_code}), 201

@api_bp.post("/attendance/scan")
@login_required
@roles_required("ADMIN", "EVENT ORGANIZER")
def api_scan():
    attendance, message = mark_registration_attendance((request.get_json() or {}).get("registration_code", ""), current_user.id)
    return jsonify({"message": message, "attendance_id": attendance.id if attendance else None}), 200 if attendance else 400

@api_bp.get("/attendance/event/<int:event_id>")
@login_required
def event_attendance(event_id):
    records = Attendance.query.filter_by(event_id=event_id).all()
    return jsonify([{"student": record.student.full_name, "email": record.student.email, "time": record.attendance_time.isoformat(), "status": record.status} for record in records])
