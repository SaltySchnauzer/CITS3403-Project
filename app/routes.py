# URL routing

from flask import render_template # This uses jinja templating - peep /app/templates
from flask import request, redirect, url_for, session, flash  # NEW: added imports - can merge the top two lines once people approve of change
from flask import render_template, request, redirect, url_for, session, flash  # NEW: for password hashing
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
import sqlalchemy as sa
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User
from app.forms import LoginForm, RegistrationForm

# -- pages --

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/session')
@login_required
def session_page():
    return render_template('session.html', title='Session')

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = db.session.scalars(sa.select(User)).all()
    return render_template('friends.html', title='Friends', leaderboard = users)

# @app.route('/history')
# @login_required
# def history():
# 	# place holder data until connected to the db
# 	weekly_data = {
# 		"Monday": 2,
# 		"Tuesday": 1.5,
# 		"Wednesday": 3,
# 		"Thursday": 0,
# 		"Friday": 2.5,
# 		"Saturday": 4,
#         "Sunday" : 1
# 	}

#     rating_data = {
#         "Monday": 4,
#         "Tuesday" 3,
#         "Wednesday": 5,
#         "Thursday": 0,
#         "Friday": 2,
#         "Saturday": 4,
#         "Sunday": 3
#     }

# 	topic_data = {
#         "Math": 5,
# 		"Science": 3,
# 		"History": 2,
# 		"Litrature": 4
# 	}



# 	return render_template('history.html', title='History', weekly_data=weekly_data, rating_data=rating_data, topic_data=topic_data)
@app.route('/history')
@login_required
def history():
    # Placeholder values
    weekly_data = {
        "Monday": 2,
        "Tuesday": 1.5,
        "Wednesday": 3,
        "Thursday": 0,
        "Friday": 2.5,
        "Saturday": 4,
        "Sunday": 1
    }

    rating_data = {
        "Monday": 4,
        "Tuesday": 3,
        "Wednesday": 5,
        "Thursday": 0,
        "Friday": 2,
        "Saturday": 4,
        "Sunday": 3
    }

    topic_data = {
        "Math": 5,
        "Science": 3,
        "History": 2,
        "Literature": 4
    }

    return render_template("history.html", 
        weekly_data=weekly_data,
        rating_data=rating_data,
        topic_data=topic_data)






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
