# ClassroomApp

A small Flask app configured to run with Docker Compose, PostgreSQL, Gunicorn, and nginx.

## First-Time Setup

Create your real `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the placeholder values:

```env
POSTGRES_DB=classroom_app
POSTGRES_USER=classroom_user
POSTGRES_PASSWORD=your-real-password
SECRET_KEY=your-long-random-secret-key
```

The real `.env` file is ignored by Git so local secrets do not get committed.

## Docker Commands

Build the web image:

```powershell
docker compose build web
```

Start the full stack:

```powershell
docker compose up
```

Start the full stack in the background:

```powershell
docker compose up -d
```

Rebuild and start after dependency or Dockerfile changes:

```powershell
docker compose up --build
```

Stop running containers:

```powershell
docker compose down
```

Stop containers and remove the Postgres volume:

```powershell
docker compose down -v
```

Use `down -v` only when you want to delete the local database data.

View container logs:

```powershell
docker compose logs
```

Follow logs live:

```powershell
docker compose logs -f
```

Follow logs for one service:

```powershell
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx
```

Check the final Compose config after `.env` values are applied:

```powershell
docker compose config
```

## App URLs

Once the stack is running, nginx exposes the app at:

```text
http://localhost:8080/
```

Health check:

```text
http://localhost:8080/health
```

## Flask Commands

Run Flask commands inside the `web` container:

```powershell
docker compose exec web flask --help
```

Open a shell inside the web container:

```powershell
docker compose exec web sh
```

Show registered routes:

```powershell
docker compose exec web flask routes
```

Open a Flask shell:

```powershell
docker compose exec web flask shell
```

## Database Commands

Open a Postgres shell inside the database container:

```powershell
docker compose exec db psql -U classroom_user -d classroom_app
```

If you changed `POSTGRES_USER` or `POSTGRES_DB` in `.env`, use those values instead.

Create the first migrations folder:

```powershell
docker compose exec web flask db init
```

Create a migration after model changes:

```powershell
docker compose exec web flask db migrate -m "describe your change"
```

Apply migrations to the database:

```powershell
docker compose exec web flask db upgrade
```

Roll back the latest migration:

```powershell
docker compose exec web flask db downgrade
```

Show migration history:

```powershell
docker compose exec web flask db history
```

Show the current database revision:

```powershell
docker compose exec web flask db current
```

## Add A Database-Backed Feature

Use this workflow when you add new tables or columns.

1. Edit your model file:

```text
app/models.py
```

2. If this is the first migration in the project, create the migrations folder:

```powershell
docker compose exec web flask db init
```

Only run `flask db init` once.

3. Generate a migration after changing models:

```powershell
docker compose exec web flask db migrate -m "add problem fields"
```

4. Apply the migration to Postgres:

```powershell
docker compose exec web flask db upgrade
```

5. Confirm the current database revision:

```powershell
docker compose exec web flask db current
```

6. Check the generated routes:

```powershell
docker compose exec web flask routes
```

## Add Test Data

Open the Flask shell:

```powershell
docker compose exec web flask shell
```

Inside the shell, add a starter problem:

```python
from app import db
from app.models import Problem

problem = Problem(
    title="Find the Off-By-One Bug",
    description="Find and explain the bug in the loop.",
    problem_type="find_bug",
    language="python",
    difficulty="easy",
    starter_code="for i in range(1, len(items)):\n    print(items[i])",
)
db.session.add(problem)
db.session.commit()
```

Query the data:

```python
Problem.query.all()
Problem.query.first().title
```

Exit the shell:

```python
exit()
```

## Add Jinja Templates

Create the template and static folders:

```powershell
New-Item -ItemType Directory -Force app\templates
New-Item -ItemType Directory -Force app\templates\problems
New-Item -ItemType Directory -Force app\static\css
```

Create common template files:

```powershell
New-Item -ItemType File -Force app\templates\base.html
New-Item -ItemType File -Force app\templates\index.html
New-Item -ItemType File -Force app\templates\problems\new.html
New-Item -ItemType File -Force app\static\css\app.css
```

Use `render_template` in Flask routes to render Jinja templates:

```python
from flask import render_template


@app.get("/")
def index():
    return render_template("index.html")
```

Pass database data into a template:

```python
from flask import render_template

from app.models import Problem


@app.get("/")
def index():
    problems = Problem.query.order_by(Problem.id.desc()).all()
    return render_template("index.html", problems=problems)
```

Loop through data in Jinja:

```html
{% for problem in problems %}
  <h2>{{ problem.title }}</h2>
  <p>{{ problem.description }}</p>
{% else %}
  <p>No problems yet.</p>
{% endfor %}
```

Link CSS from `base.html`:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/app.css') }}">
```

Link to a Flask route from a template:

```html
<a href="{{ url_for('index') }}">Home</a>
```

## Add A Form Page

Create a GET route to show the form and a POST route to save it:

```python
from flask import redirect, render_template, request, url_for

from app import db
from app.models import Problem


@app.get("/problems/new")
def new_problem():
    return render_template("problems/new.html")


@app.post("/problems")
def create_problem():
    problem = Problem(
        title=request.form["title"],
        description=request.form["description"],
        problem_type=request.form["problem_type"],
        language="python",
        difficulty=request.form["difficulty"],
        starter_code=request.form.get("starter_code"),
    )
    db.session.add(problem)
    db.session.commit()
    return redirect(url_for("index"))
```

Create the form in `app/templates/problems/new.html`:

```html
<form method="post" action="{{ url_for('create_problem') }}">
  <label for="title">Problem title</label>
  <input id="title" name="title" type="text" required>

  <label for="description">Description</label>
  <textarea id="description" name="description" required></textarea>

  <label for="problem_type">Problem type</label>
  <input id="problem_type" name="problem_type" type="text" value="write_code" required>

  <label for="difficulty">Difficulty</label>
  <select id="difficulty" name="difficulty">
    <option value="easy">Easy</option>
    <option value="medium">Medium</option>
    <option value="hard">Hard</option>
  </select>

  <label for="starter_code">Starter code</label>
  <textarea id="starter_code" name="starter_code"></textarea>

  <button type="submit">Create problem</button>
</form>
```

## Development Server Option

The current Docker command uses Gunicorn:

```yaml
command: sh -c "gunicorn --bind 0.0.0.0:5000 run:app"
```

For local development with auto-reload, temporarily change it to:

```yaml
command: sh -c "flask run --host=0.0.0.0 --port=5000 --debug"
```

Then restart the stack:

```powershell
docker compose down
docker compose up --build
```

## Local Development Without Docker

Docker is the recommended path for this project. If you run Flask directly on your machine, install Python dependencies first:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then set Flask variables and run the app:

```powershell
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"
flask run
```

Without Docker, the app falls back to a local sqlite database unless you provide a `DATABASE_URL`.

## Troubleshooting

If Docker says it cannot connect to `dockerDesktopLinuxEngine`, start Docker Desktop and wait until it says the engine is running.

If the web container cannot connect to Postgres, check that the database is healthy:

```powershell
docker compose ps
```

If dependencies changed but the app still behaves like the old image, rebuild:

```powershell
docker compose build --no-cache web
docker compose up
```

If you want a completely fresh local database, remove the volume:

```powershell
docker compose down -v
docker compose up --build
```
