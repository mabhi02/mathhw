# Question API Documentation

The Questions API provides endpoints for retrieving, creating, and managing questions in the ABTS Unified Generator system.

## Endpoints

### List Questions

```
GET /api/v1/questions/
```

Retrieves a paginated list of questions with optional filtering.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| domain | string | Filter by knowledge domain |
| complexity | string | Filter by question complexity (easy, medium, hard) |
| question_type | string | Filter by question type (e.g., multiple-choice, short-answer) |
| outline_id | string | Filter by the outline ID that generated the questions |
| keywords | array | Filter by keywords in question content |
| skip | integer | Number of records to skip for pagination (default: 0) |
| limit | integer | Maximum number of records to return (default: 100) |

#### Response

```json
{
  "items": [
    {
      "id": "string",
      "text": "string",
      "explanation": "string",
      "domain": "string",
      "cognitive_complexity": "string",
      "blooms_taxonomy_level": "string",
      "surgically_appropriate": true,
      "question_type": "string",
      "outline_id": "string",
      "options": [
        {
          "id": "string",
          "question_id": "string",
          "text": "string",
          "is_correct": true,
          "position": 0,
          "created_at": "2023-01-01T00:00:00.000Z",
          "updated_at": "2023-01-01T00:00:00.000Z"
        }
      ],
      "created_at": "2023-01-01T00:00:00.000Z",
      "updated_at": "2023-01-01T00:00:00.000Z"
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 100
}
```

### Get Question

```
GET /api/v1/questions/{question_id}
```

Retrieves a specific question by ID.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| question_id | string | The ID of the question |

#### Response

```json
{
  "id": "string",
  "text": "string",
  "explanation": "string",
  "domain": "string",
  "cognitive_complexity": "string",
  "blooms_taxonomy_level": "string",
  "surgically_appropriate": true,
  "question_type": "string",
  "outline_id": "string",
  "options": [
    {
      "id": "string",
      "question_id": "string",
      "text": "string",
      "is_correct": true,
      "position": 0,
      "created_at": "2023-01-01T00:00:00.000Z",
      "updated_at": "2023-01-01T00:00:00.000Z"
    }
  ],
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:00:00.000Z"
}
```

### Create Question

```
POST /api/v1/questions/
```

Creates a new question with options.

#### Request Body

```json
{
  "text": "string",
  "explanation": "string",
  "domain": "string",
  "cognitive_complexity": "string",
  "blooms_taxonomy_level": "string",
  "surgically_appropriate": true,
  "options": [
    {
      "text": "string",
      "is_correct": true,
      "position": 0
    }
  ]
}
```

#### Response

```json
{
  "id": "string",
  "text": "string",
  "explanation": "string",
  "domain": "string",
  "cognitive_complexity": "string",
  "blooms_taxonomy_level": "string",
  "surgically_appropriate": true,
  "question_type": "string",
  "outline_id": "string",
  "options": [
    {
      "id": "string",
      "question_id": "string",
      "text": "string",
      "is_correct": true,
      "position": 0,
      "created_at": "2023-01-01T00:00:00.000Z",
      "updated_at": "2023-01-01T00:00:00.000Z"
    }
  ],
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:00:00.000Z"
}
```

### Delete Question

```
DELETE /api/v1/questions/{question_id}
```

Deletes a question by ID.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| question_id | string | The ID of the question |

#### Response

No content (204)

### Generate Questions

```
POST /api/v1/questions/generate
```

Generates questions based on an outline or content using the agent pipeline.

#### Request Body

```json
{
  "outline_id": "string",
  "content": "string",
  "question_type": "multiple-choice",
  "complexity": "medium",
  "count": 5
}
```

#### Response

```json
{
  "questions": [
    {
      "id": "string",
      "text": "string",
      "explanation": "string",
      "domain": "string",
      "cognitive_complexity": "string",
      "blooms_taxonomy_level": "string",
      "surgically_appropriate": true,
      "question_type": "string",
      "outline_id": "string",
      "options": [
        {
          "id": "string",
          "question_id": "string",
          "text": "string",
          "is_correct": true,
          "position": 0,
          "created_at": "2023-01-01T00:00:00.000Z",
          "updated_at": "2023-01-01T00:00:00.000Z"
        }
      ],
      "created_at": "2023-01-01T00:00:00.000Z",
      "updated_at": "2023-01-01T00:00:00.000Z"
    }
  ],
  "metadata": {
    "model": "gpt-4",
    "tokens_used": 1250,
    "outline_id": "string",
    "generated_at": "2023-01-01T00:00:00.000Z"
  },
  "processing_time": 2.5
}
```

### Batch Process Questions

```
POST /api/v1/questions/batch
```

Processes a batch of question operations (create, update, delete).

#### Request Body

```json
{
  "items": [
    {
      "operation": "create",
      "data": {
        "text": "What is the primary function of the heart?",
        "domain": "cardiovascular",
        "options": [
          {"text": "Pumping blood", "is_correct": true, "position": 0},
          {"text": "Filtering blood", "is_correct": false, "position": 1}
        ]
      }
    },
    {
      "operation": "delete",
      "id": "question-123"
    }
  ]
}
```

#### Response

```json
{
  "job_id": "string",
  "status": "completed",
  "message": "Processed 2 items",
  "results": [
    {
      "index": 0,
      "operation": "create",
      "success": true,
      "id": "string",
      "data": {
        "id": "string",
        "text": "string",
        "explanation": "string",
        "domain": "string",
        "cognitive_complexity": "string",
        "blooms_taxonomy_level": "string",
        "surgically_appropriate": true,
        "question_type": "string",
        "outline_id": "string",
        "options": [
          {
            "id": "string",
            "question_id": "string",
            "text": "string",
            "is_correct": true,
            "position": 0,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
          }
        ],
        "created_at": "2023-01-01T00:00:00.000Z",
        "updated_at": "2023-01-01T00:00:00.000Z"
      }
    },
    {
      "index": 1,
      "operation": "delete",
      "success": true,
      "id": "question-123"
    }
  ]
}
```

### Get Batch Status

```
GET /api/v1/questions/batch/{job_id}
```

Get the status of a batch processing job.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| job_id | string | The ID of the batch job |

#### Response

```json
{
  "job_id": "string",
  "status": "processing",
  "message": "Processing 100 items",
  "results": [
    {
      "index": 0,
      "operation": "create",
      "success": true,
      "id": "string",
      "data": {
        "id": "string",
        "text": "string",
        "explanation": "string",
        "domain": "string",
        "cognitive_complexity": "string",
        "blooms_taxonomy_level": "string",
        "surgically_appropriate": true,
        "question_type": "string",
        "outline_id": "string",
        "options": [
          {
            "id": "string",
            "question_id": "string",
            "text": "string",
            "is_correct": true,
            "position": 0,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
          }
        ],
        "created_at": "2023-01-01T00:00:00.000Z",
        "updated_at": "2023-01-01T00:00:00.000Z"
      }
    }
  ]
}
```

### Get Question Statistics

```
GET /api/v1/questions/stats
```

Get statistics about the questions in the database.

#### Response

```json
{
  "total_questions": 100,
  "domains": {
    "cardiovascular": 25,
    "neurology": 30,
    "musculoskeletal": 45
  },
  "complexity_levels": {
    "easy": 30,
    "medium": 40,
    "hard": 30
  },
  "question_types": {
    "multiple-choice": 80,
    "short-answer": 20
  },
  "created_last_7_days": 15,
  "updated_at": "2023-01-01T00:00:00.000Z"
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found

```json
{
  "detail": "Question with ID 123 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to generate questions: Connection error"
}
``` 