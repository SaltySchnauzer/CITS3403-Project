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
4. Install [tailwind cli](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.4) (optional, only for developing css - not needed for running server)
    - Place exe in directory, and rename to `tailwindcss`
        - Should look like the following: `CITS3403-PROJECT/tailwindcss` *Note: there is no filetype*

### How to run after setup
1. Activate the venv virtual environment with `source venv/bin/activate`
2. Initialise the database with the following commands:
    1. `flask db init` - to create migrations versioning folder + .db
    2. `flask db migrate -m "Initial Models"` - to automatically create scripts to update tables to latest model definitions
    3. `flask db upgrade` - to push the latest tables to your .db
3. Run flask application with `flask run --debug`
4. Run the tailwind css compiler `./tailwindcss -i app/templates/input.css -o app/static/tailwind.css --watch`
    - This isn't neccessary if there are no CSS edits planned.

If the database begins to bug out, hard reset it by deleting the `migrations` folder and the `app/app.db` file.

### Current packages in use
- Flask
    - Our web app backend
    - Integrates Jinja templates
- python-dotenv
    - Saves environment variables between venv sessions
- Tailwind (CLI)
    - A CSS formatter
    - Typically depends on Node Package Manager - but because our backend is currently only python, we've opted for an independent cli

- need to add SQL and SQLalchemy stuff. 