import csv
import io
from datetime import date, datetime

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Attendance, Event, Registration, User
from app.services.attendance_service import mark_registration_attendance
from app.services.qr_service import create_registration_qr
from app.utils.decorators import roles_required

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return render_template("index.html", events=Event.query.order_by(Event.event_date).all())

@main_bp.get("/events")
def events():
    query = Event.query
    if request.args.get("q"):
        query = query.filter(Event.title.ilike(f"%{request.args['q']}%"))
    if request.args.get("category"):
        query = query.filter_by(category=request.args["category"])
    return render_template("events/list.html", events=query.order_by(Event.event_date).all())

@main_bp.get("/campus")
def campus():
    venue_names = ["Main Auditorium", "Innovation Lab", "Sports Complex", "Library", "Amphitheatre", "Cafeteria", "Admin Block", "Main Building"]
    venue_events = {venue: Event.query.filter(Event.venue.ilike(f"%{venue}%")).order_by(Event.event_date).all() for venue in venue_names}
    venue_payload = {venue: [{"id": event.id, "title": event.title, "category": event.category, "date": event.event_date.strftime("%d %b"), "time": event.start_time.strftime("%I:%M %p")} for event in records] for venue, records in venue_events.items()}
    return render_template("campus.html", venue_events=venue_events, venue_payload=venue_payload, events=Event.query.order_by(Event.event_date).all())

@main_bp.get("/events/<int:event_id>")
def event_detail(event_id):
    return render_template("events/detail.html", event=Event.query.get_or_404(event_id))

@main_bp.get("/verify/<code>")
def verify_pass(code):
    registration = Registration.query.filter_by(registration_code=code).first_or_404()
    return render_template("pass.html", registration=registration)

@main_bp.get("/dashboard")
@login_required
def dashboard():
    registrations = Registration.query.filter_by(user_id=current_user.id, status="ACTIVE").all()
    stats = {"events": Event.query.count(), "registrations": len(registrations), "attendance": Attendance.query.filter_by(user_id=current_user.id).count()}
    if current_user.role == "ADMIN":
        stats = {"events": Event.query.count(), "students": User.query.filter_by(role="STUDENT").count(), "registrations": Registration.query.count(), "attendance": Attendance.query.count()}
        return render_template("dashboard.html", stats=stats, registrations=registrations, all_events=Event.query.order_by(Event.event_date).all())
    assigned = Event.query.filter_by(created_by=current_user.id).order_by(Event.event_date).all()
    return render_template("dashboard.html", stats=stats, registrations=registrations, assigned=assigned, all_events=Event.query.order_by(Event.event_date).all())

@main_bp.post("/events/<int:event_id>/register")
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)
    if current_user.role != "STUDENT":
        flash("Only student accounts can register for events.", "error")
    elif Registration.query.filter_by(user_id=current_user.id, event_id=event.id).first():
        flash("You are already registered for this event.", "warning")
    elif date.today() > event.registration_deadline or event.participant_count >= event.max_participants:
        flash("Registration is closed for this event.", "error")
    else:
        registration = Registration(user_id=current_user.id, event_id=event.id)
        db.session.add(registration)
        db.session.flush()
        create_registration_qr(registration)
        db.session.commit()
        flash("Registration confirmed. Your QR pass is ready.", "success")
    return redirect(url_for("main.event_detail", event_id=event.id))

@main_bp.post("/registrations/<int:registration_id>/cancel")
@login_required
def cancel_registration(registration_id):
    registration = Registration.query.get_or_404(registration_id)
    if registration.user_id == current_user.id or current_user.role == "ADMIN":
        registration.status = "CANCELLED"
        db.session.commit()
        flash("Registration cancelled.", "success")
    return redirect(url_for("main.dashboard"))

@main_bp.route("/admin/events/new", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN")
def create_event():
    if request.method == "POST":
        event = _event_from_form(Event())
        event.created_by = current_user.id
        db.session.add(event)
        db.session.commit()
        flash("Event created.", "success")
        return redirect(url_for("main.events"))
    return render_template("events/form.html", event=None)

@main_bp.route("/admin/events/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN")
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == "POST":
        _event_from_form(event)
        db.session.commit()
        flash("Event updated.", "success")
        return redirect(url_for("main.event_detail", event_id=event.id))
    return render_template("events/form.html", event=event)

@main_bp.post("/admin/events/<int:event_id>/delete")
@login_required
@roles_required("ADMIN")
def delete_event(event_id):
    db.session.delete(Event.query.get_or_404(event_id))
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("main.events"))

def _event_from_form(event):
    event.title = request.form["title"]
    event.description = request.form["description"]
    event.category = request.form["category"]
    event.event_date = datetime.strptime(request.form["event_date"], "%Y-%m-%d").date()
    event.start_time = datetime.strptime(request.form["start_time"], "%H:%M").time()
    event.end_time = datetime.strptime(request.form["end_time"], "%H:%M").time()
    event.venue = request.form["venue"]
    event.max_participants = int(request.form["max_participants"])
    event.registration_deadline = datetime.strptime(request.form["registration_deadline"], "%Y-%m-%d").date()
    return event

@main_bp.route("/scanner", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN", "EVENT ORGANIZER")
def scanner():
    if request.method == "POST":
        _, message = mark_registration_attendance(request.form.get("registration_code", "").strip(), current_user.id)
        flash(message, "success" if "Successfully" in message else "warning")
    return render_template("scanner.html")

@main_bp.get("/reports/attendance.csv")
@login_required
@roles_required("ADMIN", "EVENT ORGANIZER")
def attendance_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Event", "Student", "Email", "Attendance time", "Status"])
    for item in Attendance.query.order_by(Attendance.attendance_time.desc()).all():
        writer.writerow([item.event.title, item.student.full_name, item.student.email, item.attendance_time.isoformat(), item.status])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=attendance-report.csv"})
