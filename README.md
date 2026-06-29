# FastAPI Lead Manager

![Tests](https://github.com/Mihail0123/fastapi_lead_manager/actions/workflows/tests.yml/badge.svg)

A small FastAPI project for managing leads.

## Tech stack

* FastAPI
* SQLAlchemy
* SQLite
* Alembic
* Pytest

## Local setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Database migrations

Apply existing migrations:

```powershell
alembic upgrade head
```

Create a new migration after changing SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "migration message"
```

Check the current database migration version:

```powershell
alembic current
```

Show migration history:

```powershell
alembic history
```

## Run the API

```powershell
uvicorn app.main:app --reload --port 8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Run tests

```powershell
pytest
```

## Main endpoints

```text
GET    /health
POST   /leads
GET    /leads
GET    /leads/count
GET    /leads/{lead_id}
PATCH  /leads/{lead_id}
DELETE /leads/{lead_id}
```

## Lead filters

List leads by status:

```text
GET /leads?status=qualified
```

List leads by source:

```text
GET /leads?source=website
```

Search leads by name, email, or company:

```text
GET /leads?search=acme
```

Use pagination:

```text
GET /leads?skip=0&limit=10
```

Count leads with filters:

```text
GET /leads/count
GET /leads/count?status=qualified
GET /leads/count?source=website
GET /leads/count?search=acme
```

## Lead statuses

Allowed lead statuses:

```text
new
contacted
qualified
lost
```

## Project notes

The application does not create database tables on startup.

Database schema changes are handled through Alembic migrations:

```text
change SQLAlchemy model
-> create migration
-> review migration file
-> apply migration with alembic upgrade head
```

Tests use a separate in-memory SQLite database and do not touch the local `leads.db`.

The local `leads.db` file is only for development and manual testing through Swagger.
