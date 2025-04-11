# ABTS Unified Generator Backend

The backend for the Agent-Based Text System (ABTS) Unified Generator, which uses AI agents to generate educational questions from outlines.

## API Documentation

The API documentation is available through multiple channels:

- **Swagger UI**: Available at `/api/docs` when the server is running
- **ReDoc**: Available at `/api/redoc` when the server is running
- **Static Documentation**: Available at `/api-docs` or `/static/docs.html`

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional, for containerized deployment)

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   cd backend
   python main.py
   ```
4. The server will be available at http://localhost:8000

### Using Docker

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. The API will be available at http://localhost:8000

## API Features

- Question generation from outlines
- Multiple question types (multiple-choice, true/false, short-answer)
- Agent-based processing pipeline
- Template-based question generation
- Outline management 