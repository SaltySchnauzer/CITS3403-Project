# URL routing

from flask import render_template # This uses jinja templating - peep /app/templates
from flask import request, redirect, url_for, session, flash  # NEW: added imports - can merge the top two lines once people approve of change
from flask import render_template, request, redirect, url_for, session, flash  # NEW: for password hashing
from flask import render_template, request, jsonify # for json req
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
import sqlalchemy as sa
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Session
from app.forms import LoginForm, RegistrationForm, SessionSummaryForm
from datetime import datetime


# -- pages --

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/session')
@login_required
def session_page():
    form = SessionSummaryForm()
    recent_sessions = current_user.sessions.order_by(Session.started_at.desc()).limit(6)
    return render_template('session.html', title='Session', form=form, recent_sessions=recent_sessions)



# --- JSON Endpoint for saving data of completed sessions --- 

@app.route("/api/sessions", methods=["POST"])
@login_required
def api_sessions():
    data = request.get_json()
    started = datetime.fromisoformat(data["started_at"].replace("Z", "+00:00"))
    ended   = datetime.fromisoformat(data["ended_at"].replace("Z", "+00:00"))

    sess = Session(
        name       = data.get("name"),
        started_at = started,
        ended_at   = ended,
        duration   = data["duration"],
        user_id    = current_user.id
    )
    db.session.add(sess)
    db.session.commit()

    return jsonify(status="success", session=sess.to_dict()), 201








@app.route("/submit-session-summary", methods=["POST"])
@login_required
def submit_session_summary():
    subject = request.form.get("subject")
    productivity = request.form.get("productivity")
    mood = request.form.get("mood")

    last_session = current_user.sessions.order_by(Session.started_at.desc()).first()

    if not last_session:
        flash("No session found to update.", "danger")
        return redirect(url_for("session_page"))

    last_session.name = subject
    last_session.productivity = int(productivity)
    last_session.mood = mood

    db.session.commit()
    flash("Session summary saved!", "success")
    return redirect(url_for("session_page"))  # reloads session page with updated inf


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = db.session.scalars(sa.select(User)).all()
    return render_template('friends.html', title='Friends', leaderboard = users)

@app.route('/history')
@login_required
def history():
    return render_template('history.html', title='History')


# --- Authentication Pages ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('signin'))
    return render_template('signup.html', title='Sign Up', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('signin'))
        login_user(user, remember=form.remember_me.data)
        return redirect('/index')
    return render_template('signin.html', title = 'Sign In', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
