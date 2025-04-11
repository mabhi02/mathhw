# ABTS Unified Generator Implementation Plan

## Objective

Create a unified agent-based text generation system with a FastAPI backend that generates questions based on specified outlines. The system will use a factory pattern for agent components, allow configuration of agent sequences via YAML files, and include system rules for prompt setup.

## Timeline

- **Weeks 1-2**: Backend framework setup and agent factory implementation
- **Weeks 3-4**: YAML configuration system and prompt engineering
- **Weeks 5-6**: Question generation system and API endpoints
- **Weeks 7-8**: Testing, optimization, and documentation

## Phase 1: Backend Setup & Agent Factory (Week 1-2)

### Task 1.1: FastAPI Backend Initialization
- Set up project structure with FastAPI framework
- Configure dependency management (requirements.txt)
- Implement logging and error handling
- Set up configuration management system

### Task 1.2: Agent Factory Pattern Implementation
- Design and implement AbstractAgent base class
- Create factory class for agent instantiation
- Implement initial agent types based on agent_definitions.yml (document_loader, question_generator, etc.)
- Add agent registration mechanism

### Task 1.3: Basic API Endpoint Setup
- Create health check endpoint
- Implement API versioning
- Set up authentication framework (if required)
- Create basic documentation with Swagger/OpenAPI

### Task 1.4: Docker Configuration
- Create Dockerfile for containerization
- Set up docker-compose for local development
- Configure environment variables
- Document container usage

## Phase 2: Configuration & Prompt Engineering (Week 3-4)

### Task 2.1: YAML Configuration System
- Implement YAML parser for agent sequences based on agent_definitions.yml structure
- Create validation system for YAML configurations
- Design and implement configuration schema matching agent_definitions.yml format
- Add configuration hot-reloading capability
- Recreate agent.yml files in the backend directory structure

### Task 2.2: System Rules Component
- Create system rules module using question_rules.yml content
- Implement system prompt templates incorporating SESATS guidelines
- Add placeholder substitution mechanism for question_rules.yml variables
- Implement rules validation against SESATS standards

### Task 2.3: Agent Communication Protocol
- Design inter-agent communication system following the agent sequence in agent_definitions.yml
- Implement message passing between agents (document_loader → question_generator → question_evaluator, etc.)
- Add pipeline processing for sequential agent operations
- Create monitoring for agent interaction

### Task 2.4: Agent State Management
- Design state persistence for agents
- Implement state transitions based on agent_definitions.yml config
- Create rollback mechanisms for failed sequences
- Add state inspection endpoints

## Phase 3: Question Generation System (Week 5-6)

### Task 3.1: Question Generator Agent
- Implement core question generation logic using the question_generator agent from agent_definitions.yml
- Add support for different question types following SESATS guidelines
- Create parameter system for question complexity levels specified in question_rules.yml
- Implement caching for generated questions

### Task 3.2: Question Templates
- Create template system for questions using the SESATS item structure from question_rules.yml
- Implement variable substitution in templates
- Add conditional logic in templates following SESATS guidelines
- Create template library with example formats from question_rules.yml

### Task 3.3: Outline Processing
- Create outline parser
- Implement hierarchical outline structure
- Add metadata support for outlines
- Create outline validation system against SESATS standards

### Task 3.4: Advanced API Endpoints
- Create question generation endpoints
- Implement batch processing
- Add filtering and pagination for results
- Create detailed API documentation

### Task 3.5: Enhanced Multi-Agent Endpoints
- Implement enhanced endpoints using OpenAI Agents SDK
- Create specialized agents for the question generation pipeline
- Build multi-step agent workflow with robust error handling
- Implement vector store search integration for knowledge retrieval
- Add endpoints for both standard and vector-assisted question generation

## Phase 4: Testing, Optimization & Documentation (Week 7-8)

### Task 4.1: Comprehensive Testing
- Implement unit tests for all agent components defined in agent_definitions.yml
- Create integration tests for agent sequences
- Add performance benchmarks
- Implement continuous integration setup

### Task 4.2: System Optimization
- Profile and optimize performance bottlenecks
- Implement caching strategies
- Add background task processing for long-running tasks
- Optimize database queries (if applicable)

### Task 4.3: Documentation
- Create comprehensive API documentation
- Add developer guides for extending the system with new agents
- Create usage examples and tutorials
- Document YAML configuration options for agent_definitions.yml and question_rules.yml

### Task 4.4: Deployment Preparation
- Create production deployment guide
- Implement proper logging and monitoring
- Add environment-specific configurations
- Create backup and recovery procedures

## Testable Deliverables by Week

### Week 1-2
- [ ] Working FastAPI application with basic endpoints
- [ ] Implemented agent factory pattern with agent types from agent_definitions.yml
- [ ] Documented API interface with Swagger
- [ ] Docker setup for local development

### Week 3-4
- [ ] YAML configuration parser with validation for agent_definitions.yml format
- [ ] System rules component using question_rules.yml for prompt engineering
- [ ] Working inter-agent communication between defined agents
- [ ] State management for agent sequences

### Week 5-6
- [ ] Question generation from simple outlines using SESATS guidelines
- [ ] Template system for different question types from question_rules.yml
- [ ] Outline processing capabilities
- [ ] Advanced API endpoints for question generation
- [ ] Enhanced multi-agent endpoints with OpenAI Agents SDK

### Week 7-8
- [ ] Test coverage > 80%
- [ ] Performance optimizations completed
- [ ] Comprehensive documentation
- [ ] Production-ready deployment configuration

## Integration with Other Components

- Frontend applications consuming the question generation API
- External NLP services for enhanced question generation
- Authentication systems for secure API access
- Monitoring and logging infrastructure
- Integration with OpenAI API as specified in agent_definitions.yml
- Vector store integration for knowledge retrieval

## Testing Strategy

### Unit Tests
- Test individual agent implementations from agent_definitions.yml
- Validate YAML configuration parsing
- Test prompt template rendering with question_rules.yml
- Verify question generation logic against SESATS standards

### Integration Tests
- Test complete agent sequences as defined in agent_definitions.yml
- Validate API endpoints behavior
- Test configuration changes and hot-reloading
- Verify error handling and recovery

### Performance Tests
- Measure question generation throughput
- Test system under high concurrent load
- Benchmark different agent configurations
- Test long-running sequences

## Dependencies

- FastAPI - Web framework for building the API
- Pydantic - Data validation and settings management
- PyYAML - YAML parsing and generation
- Uvicorn - ASGI server for FastAPI
- Python-dotenv - Environment variable management
- SQLAlchemy (optional) - ORM for database access if needed
- Pytest - Testing framework
- Docker/Docker-Compose - Containerization
- Jinja2 - Template engine for question templates
- Logging libraries (structlog, loguru) - Enhanced logging
- OpenAI API client - For communicating with OpenAI models
- OpenAI Agents SDK - For creating and managing specialized agents

## Implementation Details

### Agent Configuration Files
- Backend agent configuration files will be generated based on agent_definitions.yml
- Each agent will have its own configuration file in YAML format
- System prompts will incorporate guidelines from question_rules.yml
- Environment variables will be used for model selection as defined in agent_definitions.yml

### Question Rules Integration
- SESATS guidelines from question_rules.yml will be integrated into system prompts
- Item structure, stem format, and response options will follow SESATS standards
- Question validation will ensure compliance with SESATS guidelines
- Example questions will be used for few-shot prompting 

### Enhanced Multi-Agent Implementation
- Specialized agents will cover key steps in question generation workflow
- Nine different agent roles will be defined with specific instructions
- Vector store integration will provide domain-specific knowledge
- Robust error handling for each step in the multi-agent workflow
- Strict validation to ensure output quality and consistency 