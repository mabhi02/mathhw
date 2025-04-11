# Enhanced Endpoints API Breakdown

## Overview

`enhanced_endpoints.py` implements a FastAPI router for generating medical questions using OpenAI Agents SDK. The file orchestrates a multi-agent workflow to create high-quality, cognitively complex multiple-choice questions for medical education, particularly in cardiothoracic surgery.

## Core Components

### Configuration & Setup

- **Imports**: FastAPI components, Pydantic models, OpenAI Agents SDK, and utility libraries
- **Path Configuration**: Sets up system path to access project modules
- **Settings Import**: Imports OpenAI model configurations and prompts from settings
- **Logging**: Configures logging for debugging and monitoring
- **Router**: Creates FastAPI router with `/api/v1` prefix

### Data Models

#### Request Models

- `GenerateQuestionsRequest`: Structured request with prompt, vector query, question count, and complexity level

#### Response Models

- `QuestionContent`: Basic question structure (text, rationale, domain)
- `Option`: Multiple-choice option structure (text, isCorrect)
- `Reference`: Medical reference structure (title, section)
- `QuestionMetadata`: Question metadata (complexity, Bloom's level, surgical appropriateness)
- `MultipleChoiceQuestion`: Complete question structure with options, explanation, references, metadata
- `GenerateQuestionsResponse`: API response containing basic and formatted questions

### Vector Store Integration

`vector_store_search`: Function tool that simulates searching a vector database for relevant medical information.

### Agent Framework

#### `create_agents()` Function

Creates nine specialized agents, each with specific instructions:

1. **Document Loader**: Processes medical documents and extracts key clinical content
2. **Question Generator**: Creates high-cognitive-load questions testing surgical knowledge
3. **Question Evaluator**: Evaluates and ranks questions based on cognitive complexity
4. **Multiple Choice Formatter**: Transforms questions into multiple-choice format with exactly 3 options
5. **Contrarian Reviewer**: Critically evaluates questions to find flaws
6. **Question Improver**: Enhances questions to increase cognitive complexity
7. **Question Verifier**: Verifies clinical accuracy and cognitive complexity
8. **Surgical Situation Validator**: Validates surgical appropriateness of scenarios
9. **Final Formatter**: Formats verified questions for presentation

### Helper Functions

`extract_json_from_text()`: Extracts JSON data from agent outputs, handling various formats and potential errors.

### Core Workflow

#### `run_agent_workflow()` Function

Orchestrates the complete question generation pipeline:

1. **Knowledge Gathering**: Searches vector store with provided query (if available)
2. **Question Generation**: Creates initial questions based on prompt and knowledge
3. **Question Evaluation**: Ranks and selects best questions based on criteria
4. **Multiple-Choice Formatting**: Transforms questions into multiple-choice format
5. **Critical Review**: Identifies issues with questions
6. **Question Improvement**: Enhances questions based on review feedback
7. **Quality Verification**: Verifies cognitive complexity and clinical accuracy
8. **Surgical Validation**: Ensures scenarios are surgically appropriate
9. **Final Formatting**: Prepares questions for presentation with validated content

### API Endpoints

1. **`/generate`**: Generates questions based on custom prompt
2. **`/generate-with-vector-search`**: Generates questions using vector store knowledge

## Workflow Patterns

### Agent Communication Pattern

- Sequential agent execution with structured JSON passing between agents
- Each agent processes the output of previous agents
- Strict validation of outputs with recovery mechanisms

### Error Handling Pattern

- Comprehensive try/except blocks with detailed logging
- JSON extraction with fallbacks for different formats
- Data validation with recovery logic for missing fields

### Data Transformation Pattern

- Progressive refinement of question quality through agent pipeline
- Structured data conversion between different model formats
- Quality enforcement (e.g., exactly 3 options requirement)

### Logging Pattern

- Detailed step-by-step logging
- Performance timing for monitoring
- Multi-level logging (info, warning, error)

## Key Validation Steps

- Ensuring exactly 3 options per question
- Verifying cognitive complexity requirements
- Validating surgical appropriateness of scenarios
- Checking for complete, well-structured responses

This API demonstrates a sophisticated multi-agent orchestration for creating medical education materials with high cognitive demands, using OpenAI's Agent framework to progressively refine and validate content.
