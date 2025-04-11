# ABTS Unified Generator

A topic-specific knowledge testing agentic framework for generating educational questions

## Overview

ABTS Unified Generator is an agent-based text system for generating educational questions from outlines. It leverages AI agents to create high-quality assessment items that adhere to specific educational standards (SESATS guidelines). The system uses a factory pattern for agent components, allows configuration of agent sequences via YAML files, and includes system rules for prompt engineering.

## Architecture

The project follows a modern microservices architecture with three main components:

- **Backend**: FastAPI-based REST API that handles question generation logic
- **Frontend**: Next.js application that provides a user interface for interacting with the system
- **Configuration**: YAML-based configuration files that define agent behaviors and system rules

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│             │    │             │    │             │
│  Frontend   │◄───┤   Backend   │◄───┤   Config    │
│ (Next.js)   │    │  (FastAPI)  │    │   (YAML)    │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Components

### Backend (FastAPI)

The backend provides a robust API for generating and managing questions:

- **Agent Factory Pattern**: Creates and orchestrates different agent types
- **Pipeline System**: Executes sequences of agents for complex tasks
- **State Management**: Tracks and persists agent state with rollback capabilities
- **Template System**: Manages question templates with variable substitution
- **Outline Processing**: Parses and validates hierarchical content outlines

**Key Features:**

- Multi-step agent workflows with error handling
- Vector store integration for knowledge retrieval
- Batch processing capabilities
- Comprehensive validation against educational standards

### Config

Configuration is managed through YAML files that define:

- **Agent Definitions**: Types, roles, and behaviors of agents (`agent_definitions.yml`)
- **System Settings**: Global configuration parameters (`settings.yml`)
- **Question Rules**: Educational standards and guidelines (`question_rules.yml`)
- **Pipeline Definitions**: Sequences of agents for specific tasks

### Frontend (Next.js)

The frontend provides a modern interface for:

- Creating and managing question outlines
- Configuring question generation parameters
- Viewing and exporting generated questions
- Managing templates and agent configurations

## API

The API provides comprehensive endpoints for question generation and management:

### Questions Endpoints

- `GET /api/questions/`: Retrieve questions with advanced filtering
- `POST /api/questions/`: Create new questions
- `POST /api/questions/generate`: Generate questions using agent pipeline
- `POST /api/questions/batch`: Process batch question operations

### Agent and Pipeline Endpoints

- `GET /api/agents/types`: Get available agent types
- `POST /api/agents/{agent_type}/execute`: Execute a specific agent
- `POST /api/pipeline/execute`: Execute an agent pipeline sequence

### Template and Outline Endpoints

- `GET /api/templates/`: Get all available templates
- `POST /api/templates/{template_id}/render`: Render a template with variables
- `GET /api/outlines/`: List all available outlines
- `POST /api/outlines/upload`: Upload an outline file

### Comparison and Feedback Endpoints

- `POST /api/comparisons/`: Create a new comparison result
- `POST /api/feedback/`: Create or update user feedback for a comparison

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Docker and docker-compose (for containerized deployment)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-org/abts-unified-generator.git
cd abts-unified-generator
```

2. Set up the backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

3. Set up the frontend:

```bash
cd ../abts-generator
npm install
npm run dev
```

### Docker Deployment

For containerized deployment:

```bash
docker-compose up --build
```

## Backend Development Roadmap

Based on the implementation plan:

- **Phase 1**: Backend framework setup and agent factory implementation
- **Phase 2**: YAML configuration system and prompt engineering
- **Phase 3**: Question generation system and API endpoints
- **Phase 4**: Testing, optimization, and documentation

## License

MIT License
