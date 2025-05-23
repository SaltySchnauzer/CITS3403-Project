# Studyer

This is an in-development website aimed to provide the ability for users to track, analyse and share their study sessions with one another.

## Development
### Setup
1. Make sure you have python3 installed, and if using windows to use WSL
2. Set up a venv virtual environment to keep things nicely packaged
    1. `python3 -m venv venv`
    2. `source venv/bin/activate`
3. Install packages required with `pip install -r requirements.txt`
4. Install [tailwind cli](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.4) (optional, only for developing css - not needed for running server)
    - Place exe in directory, and rename to `tailwindcss`
        - Should look like the following: `CITS3403-PROJECT/tailwindcss` *Note: there is no filetype/suffix*

### How to run after setup
1. Activate the venv virtual environment with `source venv/bin/activate`
2. Initialise the database with the following commands (if there is no `app/app.db`):
    1. `flask db init` - to create migrations versioning folder + .db
    2. `flask db migrate -m "Initial Models"` - to automatically create scripts to update tables to latest model definitions
    3. `flask db upgrade` - to push the latest tables to your .db
3. Run flask application with `flask run --debug`
4. Run the Tailwind CSS compiler (in a separate terminal) `./tailwindcss -i app/templates/input.css -o app/static/tailwind.css --watch`
    - This isn't only necessary for updating CSS updates. Not required for simple set-up.

Exception: If the database *really* doesn't seem to be working, hard reset it by deleting the `migrations` folder and the `app/app.db` file.

### Tests
- Unit Tests: `python -m unittest tests/unit_test.py`
- Selenium Tests: `python -m unittest tests/selenium_test.py`

*Note: Selenium requires firefox to be installed in your linux subsystem - `sudo apt install firefox`*

### Current packages in use
- Flask
    - Our web app backend
    - Integrates Jinja templates
- python-dotenv
    - Saves environment variables between venv sessions
- Tailwind (CLI)
    - A CSS formatter
    - Typically depends on Node Package Manager - but because our backend is currently only python, we've opted for an independent cli
- SQLAlchemy
    - Backbone of interacting with an SQL database
- Flask-Login
    - Handles user sessions + authentication
- werkzeug-security
    - Password hashing/salting
- Flask-Migrate
    - Database migrations
- Flask-WTF
    - Webforms
    - Prevents CRSF attacks by including a secret key to authenticate it
- unittests
    - Included within python
    - Used for unit testing
- flask-moment
    - Timezone Rendering
    - Stored as UTC server-side: should adjust to client timezone.
- selenium
    - Used for testing via emulating a browser page
    - As close as you can get to testing a user experience