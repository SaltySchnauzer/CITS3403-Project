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
    return redirect(url_for("session_page"))  # reloads session page with updated info


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = db.session.scalars(sa.select(User)).all()
    return render_template('leaderboard.html', title='Friends', leaderboard=users)


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