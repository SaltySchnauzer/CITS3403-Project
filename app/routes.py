# URL routing

from flask import render_template # This uses jinja templating - peep /app/templates
from flask import request, redirect, url_for, session, flash  # NEW: added imports - can merge the top two lines once people approve of change
from flask import render_template, request, redirect, url_for, session, flash  # NEW: for password hashing
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
from app import db
from app.models import Accounts


# Fake "user database" until we set up sql
users = {}


# example user when logged in
example_user = {
    'username': 'Gordon Freeman',
    'sessions':
        [
            {'name': '', 'start': "Friday, 6:34pm", 'end': "Friday, 7:58pm", 'duration': "1:24:23"},
            {'name': 'molecules with the besties', 'start': "Thursday, 2:01pm", 'end': "Thursday, 5:14pm", 'duration': "3:13:41"},
            {'name': 'LMS Test I forgot about', 'start': "Monday, 9:53pm", 'end': "Tuesday, 1:12am", 'duration': "3:19:03"}
        ],
    'time': '14:23'
}

example_leaderboard = [
    {'username': 'Bingle', 'time': '00:00'},
    {'username': 'Jonesy Fortnite', 'time': '05:23'},
    {'username': 'Gordon Freeman', 'time': '07:57'}
]


# -- pages --

@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('signin'))
    return render_template('index.html', title='Home', user=example_user)

@app.route('/session')
def session_page():
    if 'username' not in session:
        return redirect(url_for('signin'))
    return render_template('session.html', title='Session', user=example_user)

@app.route('/leaderboard')
def leaderboard():
    if 'username' not in session:
        return redirect(url_for('signin'))
    return render_template('friends.html', title='Friends', user=example_user, leaderboard=example_leaderboard)

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('signin'))
    return render_template('history.html', title='History', user=example_user)


# --- Authentication Pages ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))

        users[username] = generate_password_hash(password)
        new_user = Accounts(user_name=username, password=users[username])
        db.session.add(new_user)     # ... 
        db.session.commit()             # should be in another function. Will fix later.  

        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('signin'))
    return render_template('signup.html', title='Sign Up')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        stored_password = users.get(username)
        if stored_password and check_password_hash(stored_password, password):
            session['username'] = username
            flash('Signed in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('signin'))
    return render_template('signin.html', title='Sign In')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('signin'))
