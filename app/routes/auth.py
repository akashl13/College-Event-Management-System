from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email", "").lower().strip()).first()
        if user and user.check_password(request.form.get("password", "")):
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for("main.dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        elif not request.form.get("full_name") or len(request.form.get("password", "")) < 6:
            flash("Add your name and a password with at least 6 characters.", "error")
        else:
            user = User(full_name=request.form["full_name"], email=email, student_id=request.form.get("student_id"))
            user.set_password(request.form["password"])
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now sign in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@auth_bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))
