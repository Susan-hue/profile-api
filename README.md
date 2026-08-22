# Profile Management App

A profile management system with a Django REST Framework backend and a React + Vite frontend. Users can sign in, view and edit their profile, and upload an avatar.

## Project Structure

```
profile-api/
├── backend/          # Django REST Framework API
│   ├── config/       # Django project settings
│   ├── profiles/     # Profiles app (models, views, serializers)
│   ├── media/        # Uploaded files (avatars)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env          # Secrets (not committed)
├── frontend/         # React + Vite client
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── .env          # Environment variables (not committed)
└── README.md
```

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your own SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if needed
npm run dev
```

The app will open at `http://localhost:5173`.

## Deploying to Vercel

The frontend is ready to deploy on Vercel. When setting up your project:

1. Point the root directory to `frontend`
2. Add an environment variable called `VITE_API_URL` with your deployed API URL (for example `https://your-api.example.com`)

That's it — Vercel will handle the rest.

## API Endpoints

| Method | Path                 | Description                     |
|--------|----------------------|---------------------------------|
| POST   | `/api/token/`        | Get an auth token               |
| GET    | `/api/profile/me/`   | Get current user's profile      |
| PUT    | `/api/profile/me/`   | Update display name             |
| POST   | `/api/profile/avatar/` | Upload a new avatar image     |

All endpoints except `/api/token/` require a `Token` header for authentication.
