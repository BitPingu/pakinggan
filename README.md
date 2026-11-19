# Pakinggan

A music tracking application that helps users organize their music library, track listening activity, and discover their listening preferences.

## Tech Stack

- **Frontend:** React, TypeScript, Vite
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic

## Getting Started

### Prerequisites

- Node.js and npm
- Python
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

## Running Tests

From the `server/` directory:

```bash
uv run pytest
```

Make sure PostgreSQL is running and the `pakinggan_test` database exists.

## Development Checks

From the project root:

```bash
npm run format:check
npm run lint
npm run build
npm run test
```

To run all checks together:

```bash
npm run check
```
