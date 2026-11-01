# Moodlog API

A Flask REST API for a personal mood tracker. Users sign up and log in with session-based authentication, then log mood entries (a 1–5 score and an optional note) that only they can view, edit or delete.

Built with Flask, Flask-RESTful, Flask-SQLAlchemy, Flask-Migrate and Flask-Bcrypt.

## Installation

Requires Python 3 and [Pipenv](https://pipenv.pypa.io/).

```bash
git clone https://github.com/JeffKibet/moodlog-api.git
cd moodlog-api
pipenv install
pipenv shell
flask db upgrade      
python seed.py        
```

The seed script creates 4 users with 15 mood entries each. Log in as `demo` with password `password123`. Running it again resets the data.

## Running the app

```bash
python app.py
```

The API runs at `http://localhost:5555`. In production, set a `SECRET_KEY` environment variable; the development default must not be used.

## Authentication

Authentication uses Flask sessions. Logging in or signing up stores the user's id in a signed session cookie, and the cookie is sent automatically on later requests. Passwords are hashed with bcrypt and never returned in any response.

Error responses use the shape `{"errors": ["message", ...]}`.

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/signup` | Create an account and log in. Body: `username`, `password` (min 8 chars), `password_confirmation` | 201 `{id, username}` | 422 (blank username, short password, mismatch, username taken) |
| POST | `/login` | Log in. Body: `username`, `password` | 200 `{id, username}` | 401 invalid credentials |
| GET | `/check_session` | Return the logged-in user | 200 `{id, username}` | 401 `{}` if not logged in |
| DELETE | `/logout` | End the session | 200 `{}` | none |

## Mood entries

All mood routes require a logged-in user (401 otherwise). Users can only see and change their own entries; requesting another user's entry returns 404.

| Method | Endpoint | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/moods?page=1&per_page=10` | List your entries, newest first, paginated (`per_page` max 50) | 200 `{items, page, per_page, total, pages}` | 401 |
| POST | `/moods` | Create an entry. Body: `mood_score` (integer 1–5), `note` (optional) | 201 the entry | 401, 422 invalid score |
| PATCH | `/moods/<id>` | Update `mood_score` and/or `note` | 200 the entry | 401, 404, 422 |
| DELETE | `/moods/<id>` | Delete an entry | 204 | 401, 404 |

An entry looks like:

```json
{
  "id": 1,
  "mood_score": 4,
  "note": "Good day",
  "logged_at": "2026-11-01T12:58:46+00:00",
  "user_id": 1
}
```

## Project structure

```
app.py          App factory, config and route registration
extensions.py   db, migrate and bcrypt instances
models.py       User and Mood models
resources/      auth.py and moods.py (Flask-RESTful resources)
migrations/     Flask-Migrate / Alembic migrations
seed.py         Sample data
```