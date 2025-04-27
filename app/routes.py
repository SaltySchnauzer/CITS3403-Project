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
        ]
}

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', user = example_user)

@app.route('/session')
def session():
    return render_template('session.html', title = 'Session', user = example_user)