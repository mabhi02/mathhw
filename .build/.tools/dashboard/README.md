# Data Kinetic Project Monitor

A real-time monitoring tool for tracking progress of the Data Kinetic project implementation.

## Features

- Visual progress tracking of tasks and subtasks
- JSON data viewer for raw data inspection
- AI benchmarks showing development efficiency
- Tabbed interface for multiple implementation plans
- Auto-refresh of data every 60 seconds

## Getting Started

### Method 1: Launch with HTTP Server (Recommended)

This method starts a Python HTTP server from the project root, which ensures all file paths work correctly:

```bash
# Make the script executable if needed
chmod +x .tools/monitor/launch_monitor_server.sh

# Run the launch script
.tools/monitor/launch_monitor_server.sh
```

The monitor will be available at: http://localhost:8080/.tools/monitor/

### Method 2: Direct File Opening

You can also open the HTML file directly:

```bash
# Make the script executable if needed
chmod +x .tools/monitor/launch_monitor.sh

# Run the launch script
.tools/monitor/launch_monitor.sh
```

Note: When opening directly as a file, the browser may have stricter security policies that can cause issues with loading data.

## Directory Structure

The monitor searches for JSON files in the `.state` directory at the project root:

```
project-root/
  ├── .state/
  │   ├── hydrogen_implementation.json
  │   ├── processor_implementation.json
  │   └── pre_processor_implementation.json
  └── .tools/
      └── monitor/
          ├── index.html
          ├── monitor.js
          ├── launch_monitor.sh
          └── launch_monitor_server.sh
```

## Usage

1. Navigate between plans using the tabs at the top of the page
2. Toggle between visual progress view and raw JSON view using the buttons in the header
3. Check AI benchmarks for performance metrics
4. The monitor automatically refreshes data every 60 seconds

## Troubleshooting

- If you see 404 errors in the console, make sure you're using the recommended HTTP server method.
- Check that JSON files exist in the `.state` directory at the project root.
- Ensure JSON files are properly formatted. 