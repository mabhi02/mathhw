#!/bin/bash

# Get the absolute path to this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Navigate to project root (assuming monitor is in .tools/monitor)
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
cd "$PROJECT_ROOT"

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python is not installed. Please install Python to use the monitor."
    exit 1
fi

# Start a simple HTTP server on port 5557
PORT=5557
echo "Starting HTTP server on port $PORT..."

# Try to use Python 3 first, then fall back to Python 2
if command -v python3 &> /dev/null; then
    echo "Launching server with Python 3..."
    (python3 -m http.server $PORT &)
elif command -v python &> /dev/null; then
    echo "Launching server with Python 2..."
    (python -m SimpleHTTPServer $PORT &)
fi

# Give the server a moment to start
sleep 1

# Open the browser to the monitor page
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "http://localhost:$PORT/.tools/monitor/index.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "http://localhost:$PORT/.tools/monitor/index.html"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start "" "http://localhost:$PORT/.tools/monitor/index.html"
else
    echo "Unsupported OS. Please open the following URL manually: http://localhost:$PORT/.tools/monitor/index.html"
fi

echo "Hydrogen Project Progress Monitor launched at http://localhost:$PORT/.tools/monitor/index.html"
echo "Press Ctrl+C to stop the server when finished."

# Wait for user to stop the server
wait 