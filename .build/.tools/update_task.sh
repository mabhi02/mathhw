#!/bin/bash
# update_task.sh - Update task status in state files
# Usage: update_task.sh [task-id] [status] "[optional note]"

TASK_ID=$1
STATUS=$2
NOTE=$3
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
STATE_DIR="../../.build/.state"

# Validate inputs
if [ -z "$TASK_ID" ] || [ -z "$STATUS" ]; then
  echo "Error: Missing required parameters"
  echo "Usage: update_task.sh [task-id] [status] \"[optional note]\""
  echo "Status options: pending, in-progress, completed, blocked"
  exit 1
fi

# Validate status
if [[ ! "$STATUS" =~ ^(pending|in-progress|completed|blocked)$ ]]; then
  echo "Error: Invalid status '$STATUS'"
  echo "Valid options: pending, in-progress, completed, blocked"
  exit 1
fi

# Determine state file path
# For task IDs with subtasks (e.g., cursor-rules-enhancements:1.1), use the main task
BASE_TASK_ID=${TASK_ID%%:*}
STATE_FILE="$STATE_DIR/${BASE_TASK_ID}.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "Error: State file for task $TASK_ID not found at $STATE_FILE"
  exit 1
fi

echo "Updating task $TASK_ID to status: $STATUS"
echo "State file: $STATE_FILE"

# Extract current status before update for comparison
if command -v jq &> /dev/null; then
  CURRENT_STATUS=$(jq -r '.status' "$STATE_FILE")
else
  CURRENT_STATUS=$(grep -o '"status": *"[^"]*"' "$STATE_FILE" | cut -d'"' -f4)
fi

# Update state file with jq if available
if command -v jq &> /dev/null; then
  # Update top-level status
  jq --arg status "$STATUS" \
     --arg timestamp "$TIMESTAMP" \
     --arg note "$NOTE" \
     '.status = $status | .last_updated = $timestamp | .notes = $note' \
     "$STATE_FILE" > "${STATE_FILE}.tmp"
     
  # Handle started_at and completed_at timestamps
  if [ "$STATUS" = "in-progress" ] && [ "$CURRENT_STATUS" != "in-progress" ]; then
    # Task is being started, set started_at
    jq --arg timestamp "$TIMESTAMP" '.started_at = $timestamp' "${STATE_FILE}.tmp" > "${STATE_FILE}.tmp2"
    mv "${STATE_FILE}.tmp2" "${STATE_FILE}.tmp"
  fi
  
  if [ "$STATUS" = "completed" ]; then
    # Task is being completed, set completed_at
    jq --arg timestamp "$TIMESTAMP" '.completed_at = $timestamp' "${STATE_FILE}.tmp" > "${STATE_FILE}.tmp2"
    mv "${STATE_FILE}.tmp2" "${STATE_FILE}.tmp"
  fi
  
  # If the task ID includes a subtask reference, update that specific subtask too
  if [[ "$TASK_ID" == *:* ]]; then
    # For subtasks like cursor-rules-enhancements:1.1, update the specific subtask
    SUBTASK_PATH=$(echo "$TASK_ID" | cut -d':' -f2-)
    
    # Split into parts (e.g., "1.1" becomes task 1.1)
    TASK_NUM=$(echo "$SUBTASK_PATH" | cut -d'.' -f1)
    SUBTASK_NUM=$(echo "$SUBTASK_PATH" | cut -d'.' -f2)
    
    # Update the specific subtask
    jq --arg status "$STATUS" \
       --arg timestamp "$TIMESTAMP" \
       --arg task "$TASK_NUM" \
       --arg subtask "$SUBTASK_NUM" \
       '.weeks[] | select(.tasks[].id == $task) | .tasks[] | select(.id == $task) | .subtasks[] | select(.id == ($task + "." + $subtask)) | .status = $status' \
       "${STATE_FILE}.tmp" > "${STATE_FILE}.tmp2"
       
    mv "${STATE_FILE}.tmp2" "${STATE_FILE}.tmp"
  fi
  
  # Finalize the update
  mv "${STATE_FILE}.tmp" "$STATE_FILE"
else
  # Fallback for systems without jq - basic sed replace
  sed -i "s/\"status\": *\"[^\"]*\"/\"status\": \"$STATUS\"/" "$STATE_FILE"
  sed -i "s/\"last_updated\": *\"[^\"]*\"/\"last_updated\": \"$TIMESTAMP\"/" "$STATE_FILE"
  
  if [ -n "$NOTE" ]; then
    # Escape special characters in NOTE for sed
    ESCAPED_NOTE=$(echo "$NOTE" | sed 's/[\/&]/\\&/g')
    sed -i "s/\"notes\": *\"[^\"]*\"/\"notes\": \"$ESCAPED_NOTE\"/" "$STATE_FILE"
  fi
fi

# Update current_focus in the state file if task is now in-progress
if [ "$STATUS" = "in-progress" ] && command -v jq &> /dev/null; then
  # Extract task and subtask details
  if [[ "$TASK_ID" == *:* ]]; then
    SUBTASK_PATH=$(echo "$TASK_ID" | cut -d':' -f2-)
    TASK_NUM=$(echo "$SUBTASK_PATH" | cut -d'.' -f1)
    SUBTASK_NUM=$(echo "$SUBTASK_PATH" | cut -d'.' -f2)
    
    # Get the subtask description
    SUBTASK_DESC=$(jq -r --arg task "$TASK_NUM" --arg subtask "$SUBTASK_NUM" \
      '.weeks[] | select(.tasks[].id == $task) | .tasks[] | select(.id == $task) | .subtasks[] | select(.id == ($task + "." + $subtask)) | .description' \
      "$STATE_FILE")
    
    # Update current_focus
    jq --arg week "week${TASK_NUM:0:1}" \
       --arg task "$TASK_NUM" \
       --arg subtask "$TASK_NUM.$SUBTASK_NUM" \
       --arg desc "$SUBTASK_DESC" \
       --arg status "$STATUS" \
       '.current_focus = {"week": $week, "task": $task, "subtask": $subtask, "description": $desc, "status": $status}' \
       "$STATE_FILE" > "${STATE_FILE}.tmp"
       
    mv "${STATE_FILE}.tmp" "$STATE_FILE"
  fi
fi

echo "✅ Successfully updated task status"
echo "Task: $TASK_ID"
echo "Status: $CURRENT_STATUS → $STATUS"
echo "Timestamp: $TIMESTAMP"
if [ -n "$NOTE" ]; then
  echo "Note: $NOTE"
fi

# Suggest next steps based on status change
echo ""
echo "Suggested next steps:"

case "$STATUS" in
  "in-progress")
    echo "- Continue working on the task"
    echo "- Consider creating a branch with: git checkout -b task/$TASK_ID"
    ;;
  "completed")
    echo "- Commit your changes with a descriptive message: [${TASK_ID}:completed] Description"
    echo "- Create a pull request if ready for review"
    echo "- Update the plan document with implementation details"
    ;;
  "blocked")
    echo "- Document the blocker in detail in the state file"
    echo "- Consider moving to another task while waiting for resolution"
    echo "- Add a blocker tag to the issue tracker if applicable"
    ;;
esac 