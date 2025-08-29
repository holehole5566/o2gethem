# O2geThem - Dating & Social Platform

A vibe coding project inspired by PTT-O2 and Dcard

![](https://i.meee.com.tw/INFrhc0.jpg)

## Features

- **User Authentication**: Register, login, and session management
- **Comment Posts**: Share and interact with posts
- **Dating Posts**: Create dating profiles and connect with others
- **Mail System**: Send and reply to messages

## Tech Stack

- **Backend**: FastAPI, PostgreSQL, Redis
- **Frontend**: React, TypeScript, Vite

## Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd o2gethem
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

3. **Run with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost
- API: http://localhost/api

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name
- `DATABASE_DSN`: Full database connection string
- `REDIS_URL`: Redis connection URL
- `SESSION_EXPIRE_MINUTES`: Session expiration time

## Development

### Backend
```bash
cd backend
pip install -e .
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

The application is containerized and ready for deployment on any Docker-compatible platform.

## License

MIT License