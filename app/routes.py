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
from datetime import datetime, timezone


def get_last_session():
    unfinished_sessions = current_user.sessions.where(Session.ended_at == None) # Get any sessions that haven't been finished
    last_session = unfinished_sessions.order_by(Session.started_at.desc()).first() # Get most recent
    if last_session is not None:
        unfinished_sessions.where(Session.id != last_session.id).delete() # Delete the others
    db.session.commit()
    return last_session

# -- pages --

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/session')
@login_required
def session_page():
    # Check if there is an already running session - if so, hide it in the template
    last_sessionID = ""
    last_session = get_last_session()
    if last_session != None:
        last_sessionID = last_session.id
    # Set up form + quick history
    form = SessionSummaryForm()
    recent_sessions = current_user.sessions.where(Session.ended_at != None).order_by(Session.started_at.desc()).limit(6)
    return render_template('session.html', title='Session', form=form, recent_sessions=recent_sessions, sessionID=last_sessionID)

# AJAX submission for session state
# Allows for the client to completely disconnect and session to stay in state/running

@app.route("/api/sessions", methods=["POST"])
@login_required
def api_sessions():
    data = request.get_json()
    match data["type"]:
        case "start": # Starts a session
            started = datetime.now(timezone.utc)
            sess = Session(
                started_at = started,
                user_id    = current_user.id
            )
            db.session.add(sess)
            db.session.commit()
        case "end": # For finishing the session - records time
            last_session = current_user.sessions.where(Session.id == data["id"]).first()

            # please do not change this timezone stuff, timezones are hell. I've lost upwards of two hours with this insanity.
            # ping saltyschnauzer if you need this explained to you
            endtime = datetime.now(timezone.utc)
            last_session.ended_at = datetime.now(timezone.utc)
            last_session.duration = (endtime - last_session.started_at.replace(tzinfo=timezone.utc)).total_seconds()

            # Set some defaults in case they don't do the form
            last_session.productivity = 50
            last_session.name = "Un-named Session"
            last_session.task_type = "Study"

            db.session.commit() # update db

            sess = last_session
        case "abort": # For cancelling a session
            last_session = current_user.sessions.order_by(Session.started_at.desc()).first()
            if last_session.ended_at == "":
                db.session.delete(last_session)
            return 204
        case "time": # For resyncing after a connection loss
            sess = current_user.sessions.where(Session.id == data["id"]).first() # get relevant session
            time = sess.started_at.isoformat() + "+00:00" # Send as a UTC time
            return jsonify(status="success", session=sess.to_dict(), start_time=time), 200
        case "check": # To check if there is a session running
            sess = get_last_session()
            if sess != None:
                return jsonify(status="active"), 200
            else:
                return jsonify(status="inactive"), 200
                
    return jsonify(status="success", session=sess.to_dict()), 201


@app.route("/submit-session-summary", methods=["POST"])
@login_required
def submit_session_summary():
    subject = request.form.get("subject")
    productivity = request.form.get("productivity")
    mood = request.form.get("mood")
    task_type = request.form.get("task_type")
    description = request.form.get("description")

    last_session = current_user.sessions.order_by(Session.started_at.desc()).first()

    if not last_session:
        flash("No session found to update.", "danger")
        return redirect(url_for("session_page"))

    last_session.name = subject
    last_session.productivity = float(productivity)
    last_session.mood = mood
    last_session.task_type = task_type
    last_session.description = description

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
