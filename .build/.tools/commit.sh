#!/bin/bash
# commit.sh - Commit changes with automatic task detection and status updates
# Usage: commit.sh [options] "Commit message"
# Options:
#   --task-id TASK_ID    Explicitly specify the task ID
#   --status STATUS      Update task status (in-progress, completed, blocked)

# Default values
TASK_ID=""
STATUS=""
MESSAGE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --task-id)
      TASK_ID="$2"
      shift 2
      ;;
    --status)
      STATUS="$2"
      shift 2
      ;;
    *)
      MESSAGE="$1"
      shift
      ;;
  esac
done

# Validate commit message
if [ -z "$MESSAGE" ]; then
  echo "Error: Commit message is required"
  echo "Usage: commit.sh [options] \"Commit message\""
  exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
  echo "Error: git command not found"
  exit 1
fi

# If no explicit task ID, try to detect it from the staged files
if [ -z "$TASK_ID" ]; then
  echo "No task ID specified, attempting to detect from staged files..."
  
  # Get list of staged files
  STAGED_FILES=$(git diff --cached --name-only)
  
  if [ -z "$STAGED_FILES" ]; then
    echo "No staged files found. Please stage files before committing."
    echo "Use: git add [file(s)] to stage files"
    exit 1
  fi
  
  # Take the first staged file and try to detect the task
  FIRST_FILE=$(echo "$STAGED_FILES" | head -n 1)
  
  # Use the detect_task.sh script to get the task ID
  if [ -f "./detect_task.sh" ]; then
    TASK_INFO=$(./detect_task.sh "$FIRST_FILE")
    # Extract task ID from the output
    DETECTED_TASK_ID=$(echo "$TASK_INFO" | grep "Task:" | cut -d'-' -f1 | awk '{print $2}')
    
    if [ -n "$DETECTED_TASK_ID" ]; then
      TASK_ID="$DETECTED_TASK_ID"
      echo "Detected task ID: $TASK_ID"
    else
      echo "Warning: Could not detect task ID automatically"
      echo "Using default format without task ID"
    fi
  else
    echo "Warning: detect_task.sh not found, cannot auto-detect task ID"
    echo "Using default format without task ID"
  fi
fi

# Scan staged files for task status comments
if [ -z "$STATUS" ]; then
  echo "Scanning staged files for task status comments..."
  
  # Look for @task:status patterns in the staged files diff
  TASK_COMMENTS=$(git diff --cached -U0 | grep -E "@task:(in-progress|completed|blocked)")
  
  if [ -n "$TASK_COMMENTS" ]; then
    # Extract the status from the first comment
    DETECTED_STATUS=$(echo "$TASK_COMMENTS" | head -n 1 | grep -Eo "(in-progress|completed|blocked)")
    
    if [ -n "$DETECTED_STATUS" ]; then
      STATUS="$DETECTED_STATUS"
      echo "Detected task status from comments: $STATUS"
    fi
  fi
fi

# Format commit message with task ID and status
FORMATTED_MESSAGE=""

if [ -n "$TASK_ID" ] && [ -n "$STATUS" ]; then
  # Include both task ID and status
  FORMATTED_MESSAGE="[$TASK_ID:$STATUS] $MESSAGE"
elif [ -n "$TASK_ID" ]; then
  # Include just task ID
  FORMATTED_MESSAGE="[$TASK_ID] $MESSAGE"
else
  # No task ID or status
  FORMATTED_MESSAGE="$MESSAGE"
fi

echo "Preparing to commit with message:"
echo "\"$FORMATTED_MESSAGE\""

# Update task status if needed
if [ -n "$TASK_ID" ] && [ -n "$STATUS" ]; then
  echo "Updating task status ($TASK_ID to $STATUS)..."
  
  if [ -f "../update_task.sh" ]; then
    ../update_task.sh "$TASK_ID" "$STATUS" "Updated via commit: $MESSAGE"
  else
    echo "Warning: update_task.sh not found, skipping status update"
  fi
fi

# Commit the changes
git commit -m "$FORMATTED_MESSAGE"
COMMIT_RESULT=$?

if [ $COMMIT_RESULT -eq 0 ]; then
  echo "✅ Changes committed successfully"
else
  echo "❌ Commit failed with error code $COMMIT_RESULT"
  exit $COMMIT_RESULT
fi

# Suggest next steps
echo ""
echo "Next steps:"

if [ "$STATUS" = "completed" ]; then
  echo "- Push your changes: git push"
  echo "- Create a pull request for task $TASK_ID"
elif [ "$STATUS" = "in-progress" ]; then
  echo "- Continue working on task $TASK_ID"
  echo "- Push your changes: git push"
else
  echo "- Push your changes: git push"
  echo "- Update task status when ready: .build/.tools/update_task.sh $TASK_ID completed \"Task completed\""
fi 