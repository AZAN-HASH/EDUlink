# EduLink

EduLink is a full-stack social and collaboration platform for high school science students, school clubs, and independent learners. The project combines profile-driven social networking, club communities, project posting, search, JWT authentication, and real-time chat/notifications.

## Stack

- Frontend: React, React Router, Axios, Socket.IO client, CSS
- Backend: Flask, Flask Blueprints, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-SocketIO
- Database: PostgreSQL
- Storage: local uploads with a cloud-ready abstraction point

## Project Structure

```text
backend/
  app/
    models/
    routes/
    schemas/
    services/
    utils/
  config.py
  app.py

frontend/
  src/
    components/
    context/
    pages/
    services/
    styles/
```

## Implemented Features

- User registration and login with JWT access and refresh tokens
- Password hashing with bcrypt and token invalidation on logout
- Role system for `student`, `club_leader`, and `admin`
- School creation and join flow
- Club creation, membership requests, approval, and group chat
- Global and following feeds with posts, comments, likes, shares, and bookmarks
- Media upload validation for images and MP4 videos
- Search across users, schools, clubs, and posts
- Direct messaging and club chat with Flask-SocketIO
- Notifications for follows, messages, comments, likes, club joins, and approvals
- Dashboard and admin overview endpoints

## Backend Setup

1. Install PostgreSQL and create a database named `edulink`.
2. Copy `backend/.env.example` to `backend/.env` and update the credentials.
3. Keep `APP_ENV=development` locally. For public deployment set `APP_ENV=production` and set strong secret values.
4. Create and activate a virtual environment.
5. Install dependencies:

```powershell
cd D:\EDUlink\backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

6. Run the backend:

```powershell
python app.py
```

The API will start on `http://localhost:5000`.
Health check endpoint: `http://localhost:5000/health`.

## Frontend Setup

1. Install Node.js 18+ so `npm` is available.
2. Copy `frontend/.env.example` to `frontend/.env`.
3. Install frontend dependencies and start Vite:

```powershell
cd D:\EDUlink\frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`.

## Important Notes

- Uploaded files are served from `http://localhost:5000/uploads/<filename>`.
- The backend creates database tables automatically on startup for development.
- For production, replace `db.create_all()` with migrations and move file storage to S3, GCS, or another object store.
- Socket and API CORS can be restricted via `CORS_ORIGINS` and `SOCKET_CORS_ORIGINS` (comma-separated).

## Verification

Backend smoke test:

```powershell
cd D:\EDUlink\backend
.venv\Scripts\python.exe smoke_test.py
```

Frontend production build:

```powershell
cd D:\EDUlink\frontend
npm run build
```

Status in this workspace:

- Backend smoke suite passes against a shared in-memory SQLite test database.
- Frontend production build completed successfully and emitted `frontend/dist`.
- `python -m compileall` is not the preferred verifier on this machine because repeated Windows `__pycache__` locking was noisy during verification.
