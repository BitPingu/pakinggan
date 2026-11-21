# pakinggan

pakinggan is a music tracking application that helps users organize their music library, track listening activity, and discover their listening preferences.

Inspired by my interest in music.

## Features

- User registration and authentication
- Forgot-password and password-reset functionality
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

### 4. Start PostgreSQL and Mailpit

From the project root:

```bash
docker compose up -d
```

This starts PostgreSQL and Mailpit.

Mailpit captures outgoing emails during local development, allowing you to test password-reset emails without sending messages to real inboxes.

The Mailpit web interface is available at:

[http://localhost:8025](http://localhost:8025)

### 5. Configure Email Delivery

The backend uses SMTP to send password-reset emails. The default configuration is set up for local Mailpit development.

The following settings can be configured in `server/.env`:

| Variable          | Default                   | Description                                        |
| ----------------- | ------------------------- | -------------------------------------------------- |
| `FRONTEND_URL`    | `http://localhost:5173`   | Frontend URL used to generate password-reset links |
| `SMTP_HOST`       | `localhost`               | SMTP server hostname                               |
| `SMTP_PORT`       | `1025`                    | SMTP server port                                   |
| `SMTP_USERNAME`   | None                      | SMTP authentication username                       |
| `SMTP_PASSWORD`   | None                      | SMTP authentication password                       |
| `SMTP_FROM_EMAIL` | `noreply@pakinggan.local` | Sender email address                               |
| `SMTP_USE_TLS`    | `false`                   | Whether to use STARTTLS                            |

For local development, the default settings work with Mailpit.

For production, configure these variables with credentials and connection details from a real SMTP email provider. Do not use Mailpit as a production email service.

### 6. Run Database Migrations

From the `server/` directory:

```bash
uv run alembic upgrade head
```

### 7. Access the Database

PostgreSQL runs in Docker. To access the database interactively, run the following command from the project root:

```bash
docker exec -it pakinggan-db psql -U pakinggan -d pakinggan
```

Once connected, you can execute SQL queries directly. For example, to view registered users:

```sql
SELECT id, username, email FROM users;
```

To exit the PostgreSQL terminal:

```text
\q
```

### 8. Start the Backend

From the `server/` directory:

```bash
uv run fastapi dev app/main.py
```

The API will be available at:

- API: [http://localhost:8000](http://localhost:8000)
- API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 9. Start the Frontend

Open a separate terminal:

```bash
cd client
npm run dev
```

The frontend will be available at:

[http://localhost:5173](http://localhost:5173)

## Scripts

All commands can be run from the project root using the root `package.json`.

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `npm run dev`          | Start the frontend development server            |
| `npm run format`       | Format project files with Prettier and Ruff      |
| `npm run format:check` | Check formatting without modifying files         |
| `npm run lint`         | Run ESLint and Ruff                              |
| `npm run build`        | Build the frontend for production                |
| `npm run test`         | Run backend tests                                |
| `npm run check`        | Run formatting checks, linting, build, and tests |

### Recommended Workflow

Run `npm run format` to format files when needed.

Run `npm run check` before committing changes to verify formatting, linting, tests, and the production build.

Make sure PostgreSQL is running and the `pakinggan_test` database has been created before running the checks.
