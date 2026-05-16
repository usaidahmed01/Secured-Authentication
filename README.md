# Secured Auth API

A production-style **FastAPI async authentication backend** built with PostgreSQL, Redis, JWT dual-token authentication, token rotation, and instant logout using Redis blacklist.

This project was developed as part of a backend assignment focused on secure authentication, async API development, automated testing, linting, security scanning, and GitHub Actions CI.

---

## Project Overview

This backend provides a secure authentication system with:

- Async FastAPI application
- PostgreSQL database using SQLAlchemy async ORM
- Redis-based token blacklist for instant logout
- Password hashing with bcrypt
- OAuth2 login flow
- Access token and refresh token generation
- Refresh token rotation
- Protected user route
- Automated async tests
- Ruff linting
- Bandit security scan
- GitHub Actions CI pipeline

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Async Python web framework |
| PostgreSQL | Relational database |
| SQLAlchemy Async | Async ORM/database interaction |
| asyncpg | Async PostgreSQL driver |
| Redis | Token blacklist storage |
| Docker | Running Redis locally |
| python-jose | JWT encoding/decoding |
| passlib + bcrypt | Password hashing |
| Pydantic | Request/response validation |
| Pytest + pytest-asyncio | Async test suite |
| HTTPX | Async API testing |
| Ruff | Linting and import formatting |
| Bandit | Static security scanning |
| GitHub Actions | Automated CI pipeline |

---

## Features

### Authentication

- User registration
- Secure password hashing
- OAuth2 form-based login
- JWT access token generation
- JWT refresh token generation
- Separate secrets for access and refresh tokens
- Refresh token rotation
- Protected route using Bearer token

### Security

- Passwords are never stored in plain text
- Access tokens are short-lived
- Refresh tokens are longer-lived
- Access and refresh tokens use separate secrets
- Every JWT contains a unique `jti`
- Logout instantly revokes the current access token
- Redis stores blacklisted access-token IDs until token expiry
- Protected routes reject revoked tokens

### Testing and Quality

- Async test client
- End-to-end authentication flow tests
- Duplicate registration test
- Invalid login test
- Invalid refresh-token test
- Ruff linting
- Bandit security scan
- GitHub Actions pipeline with PostgreSQL and Redis services

---

## Project Structure

```text
secured-auth/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   │       ├── auth.py
│   │       └── users.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   ├── redis.py
│   │   └── session.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   ├── token.py
│   │   └── user.py
│   ├── services/
│   │   ├── token_blacklist_service.py
│   │   └── user_service.py
│   ├── utils/
│   │   ├── password.py
│   │   └── token.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_auth_flow.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── create_tables.py
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/` | Root API status | No |
| GET | `/health` | Health check | No |
| POST | `/auth/register` | Register a new user | No |
| POST | `/auth/login` | Login and receive tokens | No |
| POST | `/auth/refresh` | Rotate refresh token and receive new token pair | No |
| POST | `/auth/logout` | Revoke current access token | Yes |
| GET | `/users/me` | Get current logged-in user | Yes |

---

## Authentication Flow

```text
Register user
↓
Login with email and password
↓
Receive access token and refresh token
↓
Use access token on protected routes
↓
Use refresh token when access token expires
↓
Logout stores access token jti in Redis blacklist
↓
Same access token becomes invalid immediately
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd secured-auth
```

---

### 2. Create Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
venv\Scripts\Activate.ps1
```

---

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

You can copy from `.env.example`:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
copy .env.example .env
```

Example `.env`:

```env
APP_NAME=Secured Auth API
APP_ENV=development

DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/secured_auth_db

ACCESS_TOKEN_SECRET=replace-with-random-access-secret
REFRESH_TOKEN_SECRET=replace-with-random-refresh-secret
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://localhost:6379/0
```

Generate strong JWT secrets:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Run this command twice:

- one secret for `ACCESS_TOKEN_SECRET`
- one secret for `REFRESH_TOKEN_SECRET`

---

## PostgreSQL Setup

Create a PostgreSQL database named:

```text
secured_auth_db
```

Your local database URL should look like:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/secured_auth_db
```

Create database tables:

```bash
python create_tables.py
```

Expected output:

```text
Database tables created successfully
```

---

## Redis Setup with Docker

This project uses Redis for token blacklisting.

Start Redis using Docker:

```bash
docker run --name secured-auth-redis -p 6379:6379 -d redis:7
```

Check running containers:

```bash
docker ps
```

Test Redis:

```bash
docker exec -it secured-auth-redis redis-cli ping
```

Expected output:

```text
PONG
```

If the Redis container already exists but is stopped:

```bash
docker start secured-auth-redis
```

Stop Redis:

```bash
docker stop secured-auth-redis
```

---

## Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Open in browser:

```text
http://127.0.0.1:8000
```

Swagger API docs:

```text
http://127.0.0.1:8000/docs
```

ReDoc API docs:

```text
http://127.0.0.1:8000/redoc
```

---

## Example API Usage

### Register User

```http
POST /auth/register
Content-Type: application/json
```

Request body:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:

```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-05-16T10:00:00+00:00"
}
```

---

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

Form data:

```text
username=user@example.com
password=password123
```

Response:

```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

---

### Access Protected Route

```http
GET /users/me
Authorization: Bearer <access_token>
```

Response:

```json
{
  "id": 1,
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-05-16T10:00:00+00:00"
}
```

---

### Refresh Tokens

```http
POST /auth/refresh
Content-Type: application/json
```

Request body:

```json
{
  "refresh_token": "jwt_refresh_token"
}
```

Response:

```json
{
  "access_token": "new_jwt_access_token",
  "refresh_token": "new_jwt_refresh_token",
  "token_type": "bearer"
}
```

---

### Logout

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

Response:

```json
{
  "detail": "Revocation complete"
}
```

After logout, the same access token will be rejected:

```json
{
  "detail": "Token has been revoked"
}
```

---

## Run Tests

Make sure PostgreSQL and Redis are running.

Then run:

```bash
pytest
```

Expected result:

```text
4 passed
```

---

## Run Linting

```bash
ruff check .
```

Expected result:

```text
All checks passed!
```

---

## Run Security Scan

```bash
bandit -r app
```

Expected result:

```text
No issues identified.
```

---

## Run All Local Checks

```bash
ruff check .
bandit -r app
pytest
```

---

## GitHub Actions CI

This project includes a GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

The pipeline runs automatically on:

- push to `main` or `master`
- pull requests to `main` or `master`
- manual workflow dispatch, if enabled

The CI pipeline starts:

- PostgreSQL service container
- Redis service container

Then it runs:

```text
Install dependencies
Create database tables
Run Ruff linting
Run Bandit security scan
Run Pytest tests
```

A successful pipeline shows a green checkmark in the GitHub Actions tab.

---

## Security Notes

- `.env` must never be committed to GitHub.
- Use `.env.example` for sharing required environment variables.
- Use strong random secrets for JWT signing.
- Passwords are hashed using bcrypt.
- JWTs include `jti` for revocation.
- Redis blacklist enables instant logout.
- Access and refresh tokens use different secrets.

---

## Important Commands

### Start Redis

```bash
docker start secured-auth-redis
```

### Stop Redis

```bash
docker stop secured-auth-redis
```

### Run server

```bash
uvicorn app.main:app --reload
```

### Create tables

```bash
python create_tables.py
```

### Run tests

```bash
pytest
```

### Run linting

```bash
ruff check .
```

### Run security scan

```bash
bandit -r app
```

---

## Assignment Requirements Covered

- 100% async FastAPI backend
- PostgreSQL async database integration
- OAuth2-style login endpoint
- Access token and refresh token generation
- Dual-token key separation
- Refresh token rotation
- Redis blacklist for instant logout
- Protected route with Bearer authentication
- Automated async tests
- Ruff linting
- Bandit security scan
- GitHub Actions CI pipeline

---

## Author

**Basit Ahmed**

Backend project for FastAPI OAuth2 authentication, Redis blacklist logout, PostgreSQL integration, and automated CI testing.
