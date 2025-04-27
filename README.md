# Study Tracking website

lalala description or something

## Development
### Setup
1. Make sure you have python3 installed, and if using windows to use WSL
2. Set up a venv virtual environment to keep things nicely packaged
    1. `python3 -m venv venv`
    2. `source venv/bin/activate`
3. Install packages required with `pip install -r requirements.txt`
    - This is automated for you with `requirements.txt`

### How to run after setup
1. Activate the venv virtual environment with `source venv/bin/activate`
2. Run flask application with `flask run`

### Current packages in use
- Flask
    - Our web app backend
    - Integrates Jinja templates
- python-dotenv
    - Saves environment variables between venv sessions