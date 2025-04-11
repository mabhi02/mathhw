#!/bin/bash

echo "Testing question generation..."

curl -v -X POST http://localhost:8000/api/questions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Write a question regarding the best surgical approach to his Siewert type III adenocarcinoma of the cardia in a 55-year-old man",
    "question_type": "multiple-choice", 
    "complexity": "high",
    "count": 1
  }' | tee /dev/tty | jq .
