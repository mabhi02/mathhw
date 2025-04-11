#!/bin/bash
# detect_task.sh - Detect which task a file is associated with
# Usage: detect_task.sh <file_path>

FILE_PATH=$1
STATE_DIR="../../.build/.state"
PLANS_DIR="../../.build/.plans"

# If no file path is provided, use the current directory
if [ -z "$FILE_PATH" ]; then
  FILE_PATH=$(pwd)
fi

# Define mapping patterns to search for
declare -A PATTERNS=(
  ["src/components/"]="cursor-rules-enhancements:1.3|UI Component Structure"
  ["src/utils/"]="cursor-rules-enhancements:1.2|Utility Function Organization"
  ["src/api/"]="system-enhancements:1.1|API Integration"
  ["src/hooks/"]="cursor-rules-enhancements:1.3|Custom Hook Structure"
  ["src/pages/"]="system-enhancements:1.3|Page Routing"
  ["src/styles/"]="cursor-rules-enhancements:1.2|Style Organization"
  ["src/types/"]="cursor-rules-enhancements:1.1|Type Definitions"
  ["tests/"]="cursor-rules-enhancements:2.3|Test Structure"
  [".github/"]="system-enhancements:1.3|GitHub Integration"
  [".build/"]="implementation-strategy:1.1|Build System Integration"
  ["blocks/"]="cursor-rules-enhancements:1.1|Cursor Rules Development"
)

# Check for TypeScript/JavaScript files
if [[ "$FILE_PATH" =~ \.(ts|tsx|js|jsx)$ ]]; then
  LANGUAGE="TypeScript/JavaScript"
  
  # Special detection for component files
  if [[ "$FILE_PATH" =~ components/ && "$FILE_PATH" =~ \.(tsx|jsx)$ ]]; then
    TASK_ID="cursor-rules-enhancements:1.3"
    TASK_DESC="UI Component Structure"
  fi
  
  # Special detection for utility files
  if [[ "$FILE_PATH" =~ utils/ && "$FILE_PATH" =~ \.(ts|js)$ ]]; then
    TASK_ID="cursor-rules-enhancements:1.2"
    TASK_DESC="Utility Function Organization"
  fi
  
  # Special detection for type files
  if [[ "$FILE_PATH" =~ types/ && "$FILE_PATH" =~ \.ts$ ]]; then
    TASK_ID="cursor-rules-enhancements:1.1"
    TASK_DESC="Type Definitions"
  fi
  
  # Test file detection
  if [[ "$FILE_PATH" =~ \.(test|spec)\.(ts|tsx|js|jsx)$ ]]; then
    TASK_ID="cursor-rules-enhancements:2.3"
    TASK_DESC="Test Coverage Rules"
  fi
fi

# Check for Python files
if [[ "$FILE_PATH" =~ \.py$ ]]; then
  LANGUAGE="Python"
  
  # Special detection for test files
  if [[ "$FILE_PATH" =~ test_ || "$FILE_PATH" =~ _test ]]; then
    TASK_ID="cursor-rules-enhancements:2.3"
    TASK_DESC="Test Coverage Rules"
  else
    TASK_ID="cursor-rules-enhancements:1.1"
    TASK_DESC="Python File Organization"
  fi
fi

# If no specific rule matched, search by directory pattern
if [ -z "$TASK_ID" ]; then
  for PATTERN in "${!PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == *"$PATTERN"* ]]; then
      IFS='|' read -r TASK_ID TASK_DESC <<< "${PATTERNS[$PATTERN]}"
      break
    fi
  done
fi

# If still no match, use a default
if [ -z "$TASK_ID" ]; then
  TASK_ID="implementation-strategy:1.1"
  TASK_DESC="General Implementation"
fi

# Get task status from state file
STATE_FILE="$STATE_DIR/${TASK_ID/%:*}.json"
if [ -f "$STATE_FILE" ]; then
  # Extract status using jq if available
  if command -v jq &> /dev/null; then
    STATUS=$(jq -r '.status' "$STATE_FILE")
    LAST_UPDATED=$(jq -r '.last_updated' "$STATE_FILE")
    NOTES=$(jq -r '.notes' "$STATE_FILE")
  else
    # Simple grep fallback if jq is not available
    STATUS=$(grep -o '"status": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
    LAST_UPDATED=$(grep -o '"last_updated": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
    NOTES=$(grep -o '"notes": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
  fi
else
  STATUS="unknown"
  LAST_UPDATED="unknown"
  NOTES="State file not found"
fi

# Output the results
echo "File: $FILE_PATH"
echo "Language: $LANGUAGE"
echo "----------------"
echo "Task: $TASK_ID - $TASK_DESC"
echo "Status: $STATUS"
echo "Last Updated: $LAST_UPDATED"
echo "Notes: $NOTES"
echo "----------------"
echo "Related state file: $STATE_FILE"

# Suggest next files
echo ""
echo "Suggested related files:"

case "$TASK_ID" in
  "cursor-rules-enhancements:1.1")
    echo "- blocks/typescript.md (Language-specific rules)"
    echo "- blocks/python.md (Language-specific rules)"
    echo "- blocks/task_context.md (Context-aware task detection)"
    ;;
  "cursor-rules-enhancements:1.3")
    echo "- blocks/task_context.md (Context-aware task detection)"
    echo "- blocks/typescript.md (TypeScript component structure)"
    ;;
  "cursor-rules-enhancements:2.3")
    echo "- blocks/test_coverage.md (Test coverage rules)"
    echo "- blocks/.tools/create_test.sh (Test creation tool)"
    ;;
  *)
    echo "- blocks/task_context.md (Context-aware task detection)"
    echo "- staging/cursor_rules_enhancements.md (Implementation plan)"
    ;;
esac 