# URL routing

from flask import render_template # This uses jinja templating - peep /app/templates
from app import app

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

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', user = example_user)

@app.route('/session')
def session():
    return render_template('session.html', title = 'Session', user = example_user)

@app.route('/leaderboard')
def leaderboard():
    return render_template('friends.html', title = 'Friends', user = example_user, leaderboard = example_leaderboard)

@app.route('/history')
def history():
    return render_template('history.html', title = 'History', user = example_user)