#!/bin/bash

echo "Testing question preview generation..."

curl -v -X POST http://localhost:8000/api/questions/generate/preview \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Write a question regarding diagnostic criteria for acute cholecystitis",
    "question_type": "multiple-choice", 
    "complexity": "medium",
    "count": 1
  }' | tee /dev/tty | jq . 