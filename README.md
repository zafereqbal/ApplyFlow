# ApplyFlow — Full-Stack Job Application Tracker

ApplyFlow is a full-stack web application for organizing job applications, tracking interview stages, and reviewing job-search progress through a simple analytics dashboard.

> **Portfolio project:** Built to demonstrate backend engineering, REST API design, authentication, relational databases, caching, automated testing, containerization, and frontend integration.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Run with Docker](#run-with-docker)
- [Run the Backend Locally](#run-the-backend-locally)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Security and Engineering Notes](#security-and-engineering-notes)
- [Roadmap](#roadmap)
- [Resume Description](#resume-description)

## Features

### Authentication and authorization
- Account registration and login
- Password hashing with Argon2
- JWT-protected endpoints
- User-scoped application access so one user cannot retrieve another user's applications

### Application management
- Create, list, update, and delete job applications
- Track stages: `saved`, `applied`, `screening`, `interview`, `offer`, `rejected`, and `withdrawn`
- Search by company or role
- Filter by status
- Paginate and sort results
- Validate inputs and salary ranges

### Dashboard and performance
- Application totals and counts by status
- Interview-pipeline rate and offer count
- Redis cache for dashboard summaries
- Cache invalidation after application changes
- Graceful fallback to uncached summaries if Redis is unavailable

### Frontend
- React and TypeScript dashboard
- Sign-up and sign-in forms
- Quick-add application form
- Status updates and application deletion
- Search and visual pipeline chart
- Responsive layout

### Engineering workflow
- Docker Compose for the API, PostgreSQL, Redis, and frontend
- Pytest API tests
- GitHub Actions CI workflow
- FastAPI interactive API documentation

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Validation | Pydantic |
| Authentication | JWT, Argon2 password hashing |
| ORM and database access | SQLAlchemy |
| Database | PostgreSQL |
| Cache | Redis |
| Frontend | React, TypeScript, Vite |
| Charts | Recharts |
| Tests | Pytest, HTTPX |
| Containers | Docker, Docker Compose |
| CI | GitHub Actions |

## Architecture

```text
React + TypeScript (Vite)
          |
          | HTTP / JSON + Bearer token
          v
      FastAPI API
       /   |    \
      /    |     \
 Auth   Applications   Dashboard
          |                |
          v                v
     PostgreSQL          Redis cache
```

The API owns validation and authorization. SQLAlchemy persists users and applications in PostgreSQL. Dashboard summaries are cached in Redis with a short time-to-live; application mutations invalidate the relevant user's cached summary.

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- Git, if cloning the repository
- Alternatively: Python 3.12+, Node.js 22+, PostgreSQL, and Redis for a manual setup

### Run with Docker

1. Extract the project archive and open a terminal in the `ApplyFlow` directory.
2. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and replace `SECRET_KEY` with a long, random secret. Do not commit `.env`.
4. Start the application:

   ```bash
   docker compose up --build
   ```

5. Open the application:

   - **Frontend:** http://localhost:5173
   - **API docs:** http://localhost:8000/docs
   - **Health endpoint:** http://localhost:8000/health

To stop the containers, press `Ctrl+C`, then run `docker compose down`. To also remove the local database volume, run `docker compose down -v` (this deletes local database data).

### Run the backend locally

For local backend development, create a virtual environment:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Set these environment variables in the shell or in a `.env` file in the working directory:

```bash
export DATABASE_URL="sqlite:///./applyflow.db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="replace-with-a-long-random-secret"
export CORS_ORIGINS="http://localhost:5173"
```

Start the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000. If Redis is not running, dashboard analytics should fall back to a database query.

### Run the frontend locally

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server is available at http://localhost:5173. Set `VITE_API_BASE_URL` if the API is hosted somewhere other than `http://localhost:8000`.

## API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `GET` | `/health` | Health check | No |
| `POST` | `/api/auth/register` | Create an account | No |
| `POST` | `/api/auth/login` | Obtain an access token | No |
| `GET` | `/api/auth/me` | Get current user | Yes |
| `POST` | `/api/applications` | Create an application | Yes |
| `GET` | `/api/applications` | List, search, filter, paginate, and sort | Yes |
| `GET` | `/api/applications/{id}` | Get an application | Yes |
| `PATCH` | `/api/applications/{id}` | Update an application | Yes |
| `DELETE` | `/api/applications/{id}` | Delete an application | Yes |
| `GET` | `/api/dashboard/summary` | Get dashboard analytics | Yes |

### Example: create an application

```json
{
  "company": "Example Corp",
  "role": "Backend Engineer",
  "job_url": "https://example.com/jobs/123",
  "status": "applied",
  "location": "Remote",
  "salary_min": 1200000,
  "salary_max": 1800000,
  "notes": "Python, FastAPI, PostgreSQL"
}
```

### Example query parameters

```text
GET /api/applications?q=backend&status=interview&page=1&page_size=10&sort=updated_at
```

For authenticated endpoints, send:

```text
Authorization: Bearer <access_token>
```

The login endpoint uses form fields `username` (the account email) and `password`, as expected by FastAPI's OAuth2 password form.

## Testing

Install the backend development dependencies, then run:

```bash
cd backend
pytest -q
```

The included tests cover registration/login, protected endpoints, application creation and updates, listing/filtering, health checks, and user-level access isolation.

Run lint checks with:

```bash
ruff check app tests
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `APP_NAME` | API title |
| `ENVIRONMENT` | Environment label |
| `SECRET_KEY` | JWT signing secret; change it before deployment |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime |
| `DATABASE_URL` | SQLAlchemy database connection URL |
| `REDIS_URL` | Redis connection URL |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `VITE_API_BASE_URL` | API base URL used by the frontend |

## Project Structure

```text
ApplyFlow/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── applications.py
│   │   │   └── dashboard.py
│   │   ├── cache.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── security.py
│   ├── migrations/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/ci.yml
├── .env.example
├── docker-compose.yml
└── README.md
```

## Security and Engineering Notes

This is a portfolio starter, not a production security audit. Before handling real users or deploying publicly, consider:

- Use a strong secret from the hosting provider's secret manager.
- Add login and registration rate limiting.
- Implement refresh-token rotation and a clear token-storage/CSRF strategy.
- Add email verification and password reset flows.
- Configure production CORS origins explicitly.
- Add structured logs, metrics, monitoring, and database backups.
- Create and verify an initial Alembic migration before relying on migrations in deployment.
- Add frontend error states, accessibility checks, and end-to-end tests.
- Run dependency and container vulnerability checks.

For quick local startup, the API creates tables at application startup. The Alembic folder is scaffolding; generate and review an initial migration before using migrations as the deployment schema-management process.

## Roadmap

- [ ] Interview calendar and reminders
- [ ] Resume versions linked to applications
- [ ] CSV export/import
- [ ] Email notifications
- [ ] Background tasks for reminders
- [ ] Rate limiting and refresh-token rotation
- [ ] End-to-end tests
- [ ] Live deployment with screenshots and a public demo
- [ ] Load test dashboard endpoints and document measured results

## Resume Description

Use this only after you have run and verified the relevant features:

**ApplyFlow — Full-Stack Job Application Tracker** | Python, FastAPI, React, TypeScript, PostgreSQL, Redis, Docker

- Built a multi-user job application tracking platform with JWT authentication, password hashing, and user-scoped REST APIs using FastAPI.
- Implemented application CRUD, search, filtering, pagination, and status analytics backed by PostgreSQL and SQLAlchemy.
- Added Redis caching for dashboard summaries and invalidation after application mutations.
- Developed a responsive React/TypeScript dashboard and added API integration tests, Docker Compose services, and a GitHub Actions CI workflow.

**Important:** Do not claim a public deployment, measured performance improvements, or passing test results until you have actually completed and verified them.
