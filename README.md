# Data Archival Service

Move old data out of your primary MySQL database, keep it around in archival storage for a while, then purge it when you don't need it anymore. All automated.

## High Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   ORCHESTRATOR (FastAPI)                                            │
│   ├── REST API for config management                                │
│   ├── Scheduler (APScheduler cron jobs)                             │
│   └── Container Manager (spawns workers via Docker SDK)             │
│                                                                     │
│           │                                                         │
│           │ spawns                                                  │
│           ▼                                                         │
│                                                                     │
│   WORKER CONTAINERS (short-lived)                                   │
│   ├── Archival Engine: moves data from Primary → Archival DB        │
│   └── Purge Engine: deletes old data from Archival DB               │
│                                                                     │
│           │                          │                              │
│           ▼                          ▼                              │
│                                                                     │
│   ┌──────────────┐              ┌──────────────┐                    │
│   │  Primary DB  │  ─────────▶  │ Archival DB  │                    │
│   │  (source)    │   archived   │  (target)    │                    │
│   └──────────────┘    data      └──────────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**How it works:**
- You configure which tables to archive and how old data should be before moving it
- The scheduler runs on a cron schedule (default: 2 AM for archival, 3 AM for purge)
- Each job spawns an isolated Docker container that does the actual work
- Workers insert data into archival DB, then delete from primary (all in a transaction)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- That's it. Everything else runs in containers.

### Build

First, build the Docker images:

```bash
cd archival-service

# make the build script executable
chmod +x build/build.sh

# build everything
./build/build.sh all
```

Or if you only want to build specific images:

```bash
./build/build.sh orchestrator   # just the orchestrator
./build/build.sh worker         # just the worker
```

### Run

Start all services with docker-compose:

```bash
docker-compose up -d
```

This starts:
- **orchestrator** - the main API service on port 8000
- **orchestrator-db** - MySQL database for storing configs
- **primary-db** - sample source database (with test data)
- **archival-db** - target database for archived data

Check everything is running:

```bash
docker-compose ps
```

### Verify

Hit the health endpoint:

```bash
curl http://localhost:8000/health
```

Open the API docs: http://localhost:8000/docs

### Stop

```bash
docker-compose down
```

Add `-v` if you want to wipe the database volumes too:

```bash
docker-compose down -v
```

## Basic Usage

### 1. Get an auth token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "roles": ["admin"]}'
```

Save the `access_token` from the response.

### 2. Create an archival config

```bash
curl -X POST http://localhost:8000/api/v1/config/archival \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_db_host": "primary-db",
    "primary_db_port": 3306,
    "primary_db_name": "production",
    "primary_db_user": "root",
    "primary_db_password": "primarypassword",
    "archival_db_host": "archival-db",
    "archival_db_port": 3306,
    "archival_db_name": "archival_data",
    "archival_db_user": "root",
    "archival_db_password": "archivalpassword",
    "table_name": "orders",
    "date_column": "created_at",
    "archival_days": 180,
    "deletion_days": 730,
    "enabled": true
  }'
```

### 4. Check what happened

```bash
# view archived data (need table role or admin)
curl http://localhost:8000/api/v1/archive/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Configuration

### Environment Variables

Set these in a `.env` file or pass them to docker-compose:

| Variable | What it does | Default |
|----------|--------------|---------|
| `JWT_SECRET_KEY` | Secret for signing tokens | - |
| `ENCRYPTION_KEY` | Encrypts stored DB passwords | - |
| `ARCHIVAL_JOB_CRON` | When to run archival | `0 2 * * *` |
| `PURGE_JOB_CRON` | When to run purge | `0 3 * * *` |
| `WORKER_IMAGE` | Docker image for workers | `das-worker:latest` |

Generate an encryption key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Project Structure

```
archival-service/
├── orchestrator/          # main API service
│   ├── main.py            # FastAPI app
│   ├── router/            # API endpoints
│   ├── scheduler/         # cron jobs + docker management
│   ├── security/          # JWT, encryption
│   └── ...
├── worker/                # archival/purge worker
│   ├── main.py            # CLI entry point
│   └── service/           # archival + purge engines
├── build/                 # build scripts
├── scripts/               # SQL init scripts
└── docker-compose.yml
```