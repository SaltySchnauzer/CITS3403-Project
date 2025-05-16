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
from app.forms import LoginForm, RegistrationForm, SessionSummaryForm, FriendSearchForm
from datetime import datetime, timezone, timedelta, date




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
    return redirect(url_for("session_page"))  # reloads session page with updated info








@app.route('/analytics')
@login_required
def analytics():
    sessions = current_user.sessions.all()

    today = date.today()
    weekly_data = {}
    for i in range(7):
        day = today - timedelta(days=6 - i)
        total_ms = sum(
            (s.duration or 0)
            for s in sessions
            if s.ended_at and s.started_at.date() == day
        )
        # ← divide by 60 000 to get minutes
        weekly_data[day.isoformat()] = round(total_ms / 60_000, 2)

    rating_data = {}
    for i in range(7):
        day = today - timedelta(days=6 - i)
        vals = [
            s.productivity
            for s in sessions
            if s.ended_at
               and s.started_at.date() == day
               and s.productivity is not None
        ]
        rating_data[day.isoformat()] = round(sum(vals) / len(vals), 2) if vals else 0

    # pie by subject name now
    subject_data = {}
    for s in sessions:
        if s.ended_at and s.name:
            mins = (s.duration or 0) / 60_000
            subject_data[s.name] = subject_data.get(s.name, 0) + mins

    return render_template(
        'analytics.html',
        weekly_data=weekly_data,
        rating_data=rating_data,
        topic_data=subject_data    # renamed to subject_data
    )













@app.route('/history')
@login_required
def history():
    return render_template('history.html', title='History')


# --- AJAX/Friend-request Endpoints ---

@app.route('/friends/search')
@login_required
def friends_search():
    q = request.args.get('q', '').strip()
    if len(q) < 1:
        return jsonify([])
    matches = User.query.filter(
        User.username.ilike(f'%{q}%'),
        User.id != current_user.id
    ).limit(10).all()
    return jsonify([{'id': u.id, 'username': u.username} for u in matches])


@app.route('/friends/add', methods=['POST'])
@login_required
def friends_add():
    data = request.get_json() or {}
    target = User.query.get(data.get('user_id'))
    if not target:
        return jsonify({'error': 'User not found'}), 404
    if target.id == current_user.id:
        return jsonify({'error': "You can't add yourself"}), 400
    if not current_user.shared_with.filter_by(id=target.id).first():
        current_user.shared_with.append(target)
        db.session.commit()
    return jsonify({'success': True, 'username': target.username})


@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
    form = FriendSearchForm()

    # — POST: add a friend by username —
    if form.validate_on_submit():
        other = User.query.filter_by(username=form.username.data).first()
        if not other:
            flash('User not found.', 'warning')
        elif other.id == current_user.id:
            flash("You can’t add yourself.", 'warning')
        else:
            current_user.add_friend(other)
            db.session.commit()
            flash(f"You are now sharing with {other.username}!", 'success')
        return redirect(url_for('friends'))

    # — GET: only mutual sharing (true “friends”) —
    shared_ids  = {u.id for u in current_user.shared_with}
    sharers_ids = {u.id for u in current_user.shared_by}
    mutual_ids  = shared_ids & sharers_ids
    friends     = User.query.filter(User.id.in_(mutual_ids)).order_by(User.username).all()

    # pick selected friend by ?friend_id= or default to the first one
    fid = request.args.get('friend_id', type=int)
    if not fid and friends:
        fid = friends[0].id
    selected = User.query.get_or_404(fid) if fid else None

    # —— analytics computation —— 
    total_sessions = 0
    total_time_ms   = 0
    avg_duration_ms = 0

    # distribution buckets
    prod_labels = [0, 25, 50, 75, 100]
    prod_counts = [0] * len(prod_labels)
    mood_labels = ['sad', 'neutral', 'happy']
    mood_counts = [0] * len(mood_labels)

    if selected:
        sessions = selected.sessions.order_by(Session.started_at).all()
        total_sessions = len(sessions)
        total_time_ms = sum(s.duration for s in sessions)
        avg_duration_ms = (total_time_ms // total_sessions) if total_sessions else 0

        for s in sessions:
            if s.productivity in prod_labels:
                prod_counts[prod_labels.index(s.productivity)] += 1
            if s.mood in mood_labels:
                mood_counts[mood_labels.index(s.mood)] += 1

    # convert to human units
    total_hours = round(total_time_ms / 3_600_000, 2)   # ms → hours
    avg_minutes = round(avg_duration_ms / 60_000, 1)    # ms → minutes

    return render_template(
        'friends.html',
        title='Friends',
        form=form,
        friends=friends,
        selected=selected,
        total_sessions=total_sessions,
        total_hours=total_hours,
        avg_minutes=avg_minutes,
        productivity_data={
            'labels': prod_labels,
            'counts': prod_counts
        },
        mood_data={
            'labels': mood_labels,
            'counts': mood_counts
        }
    )


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
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('signin'))
        login_user(user, remember=form.remember_me.data)
        return redirect('/index')
    return render_template('signin.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))