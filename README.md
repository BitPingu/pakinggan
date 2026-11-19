# pakinggan

pakinggan is a music tracking application that helps users organize their music library, track listening activity, and discover their listening preferences.

Inspired by my interest in music.

## Features

- User registration and authentication
- Music library management for artists, albums, and tracks
- Dashboard with an overview of your music library

## Tech Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic

## Project Structure

```text
pakinggan/
├── client/    # React frontend
└── server/    # FastAPI backend
```

## Getting Started

### Prerequisites

- Node.js (22 or later)
- npm
- Python (3.12 or later)
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop

### 1. Clone the Repository

```bash
git clone https://github.com/BitPingu/pakinggan.git
cd pakinggan
```

### 2. Configure the Backend

Create a `server/.env` file using `server/.env.example` as a template. Configure your database URL and JWT secret.

Install dependencies:

```bash
cd server
uv sync
```

### 3. Configure the Frontend

Create a `client/.env` file using `client/.env.example` as a template.

Install dependencies:

```bash
cd client
npm install
```

### 4. Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

### 5. Run Database Migrations

From the `server/` directory:

```bash
uv run alembic upgrade head
```

### 6. Start the Backend

From the `server/` directory:

```bash
uv run fastapi dev app/main.py
```

The API will be available at:

- API: http://localhost:8000
- API documentation: http://localhost:8000/docs

### 7. Start the Frontend

Open a separate terminal:

```bash
cd client
npm run dev
```

The frontend will be available at:

http://localhost:5173

## Scripts

All commands can be run from the project root using the root `package.json`.

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `npm run dev`          | Start the frontend development server            |
| `npm run format`       | Format project files with Prettier               |
| `npm run format:check` | Check formatting without modifying files         |
| `npm run lint`         | Run ESLint and Ruff                              |
| `npm run build`        | Build the frontend for production                |
| `npm run test`         | Run backend tests                                |
| `npm run check`        | Run formatting checks, linting, build, and tests |

### Recommended Workflow

Run `npm run format` to format files when needed.

Run `npm run check` before committing changes to verify formatting, linting, tests, and the production build.

Make sure PostgreSQL is running and the `pakinggan_test` database exists before running the checks.
