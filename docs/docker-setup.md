# Docker Setup for ABTS Unified Generator

This document outlines how to set up and run the ABTS Unified Generator using Docker.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (for LLM functionality)

## Development Setup

### 1. Set up environment variables

Copy the example environment file and update it with your API keys and settings:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key-here
```

### 2. Build and start the development environment

```bash
docker-compose up --build
```

This will:
- Build the backend API container
- Start a PostgreSQL database container
- Mount your local code as a volume to enable hot reloading

The API will be available at http://localhost:8000, with the documentation at http://localhost:8000/api/docs

## Production Setup

For production deployments, use the production configuration:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

Note that in production mode:
- Environment variables must be properly set in the host environment or via secrets management
- The API runs with multiple workers for better performance
- Debug mode is disabled
- Resource limits are set on containers
- Containers have health checks configured

## Container Management

### View logs

```bash
# All logs
docker-compose logs -f

# Only API logs
docker-compose logs -f api
```

### Stop containers

```bash
docker-compose down
```

### Remove volumes (caution: destroys database data)

```bash
docker-compose down -v
```

## Database Management

### Run migrations

```bash
docker-compose exec api alembic upgrade head
```

### Create a migration

```bash
docker-compose exec api alembic revision --autogenerate -m "migration description"
```

## Troubleshooting

### Database connection issues

Ensure the database container is healthy:

```bash
docker-compose ps
```

If the database doesn't come up properly, check its logs:

```bash
docker-compose logs db
```

### API errors

Check the API logs:

```bash
docker-compose logs api
```

If there are package dependency issues, rebuild the API container:

```bash
docker-compose build --no-cache api
docker-compose up -d
``` 