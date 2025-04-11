#!/bin/bash
# create_test.sh - Generate test files for implementation files
# Usage: create_test.sh [implementation_file_path]

IMPLEMENTATION_FILE=$1
TEST_ROOT="tests"

# Validate input
if [ -z "$IMPLEMENTATION_FILE" ] || [ ! -f "$IMPLEMENTATION_FILE" ]; then
  echo "Error: Invalid implementation file path"
  echo "Usage: create_test.sh [implementation_file_path]"
  exit 1
fi

# Determine file type and appropriate test patterns
FILE_EXT="${IMPLEMENTATION_FILE##*.}"
FILE_NAME=$(basename "$IMPLEMENTATION_FILE")
FILE_NAME_WITHOUT_EXT="${FILE_NAME%.*}"
DIR_PATH=$(dirname "$IMPLEMENTATION_FILE")

# Create test file path based on file type
case "$FILE_EXT" in
  "ts"|"tsx"|"js"|"jsx")
    # For TypeScript/JavaScript files
    # Check if this is a component file (in src/components)
    if [[ "$IMPLEMENTATION_FILE" == *"/components/"* ]]; then
      # For React components
      TEST_DIR="$DIR_PATH/__tests__"
      TEST_FILE="$TEST_DIR/${FILE_NAME_WITHOUT_EXT}.test.${FILE_EXT}"
      TEST_FRAMEWORK="React Testing Library"
    else
      # For utilities and other TS/JS files
      TEST_DIR="$DIR_PATH/__tests__"
      TEST_FILE="$TEST_DIR/${FILE_NAME_WITHOUT_EXT}.test.${FILE_EXT}"
      TEST_FRAMEWORK="Jest"
    fi
    ;;
    
  "py")
    # For Python files
    TEST_DIR="tests/$(echo $DIR_PATH | sed 's/^src\///')"
    TEST_FILE="$TEST_DIR/test_${FILE_NAME_WITHOUT_EXT}.py"
    TEST_FRAMEWORK="pytest"
    ;;
    
  *)
    echo "Error: Unsupported file type .$FILE_EXT"
    echo "Supported file types: .ts, .tsx, .js, .jsx, .py"
    exit 1
    ;;
esac

# Create test directory if it doesn't exist
mkdir -p "$TEST_DIR"

echo "Creating test file for: $IMPLEMENTATION_FILE"
echo "Test file: $TEST_FILE"
echo "Test framework: $TEST_FRAMEWORK"

# Extract function/class names from implementation file for test generation
FUNCTION_NAMES=()

case "$FILE_EXT" in
  "ts"|"tsx"|"js"|"jsx")
    # Extract function names from TypeScript/JavaScript files
    if command -v grep &> /dev/null; then
      # Extract function/class exports
      EXPORTS=$(grep -E '(export|function|\s*class)' "$IMPLEMENTATION_FILE" | grep -v 'import')
      
      # Extract function names using regex
      while read -r line; do
        if [[ "$line" =~ export[[:space:]]+(function|const|class)[[:space:]]+([a-zA-Z0-9_]+) ]]; then
          FUNCTION_NAMES+=("${BASH_REMATCH[2]}")
        elif [[ "$line" =~ export[[:space:]]+default[[:space:]]+([a-zA-Z0-9_]+) ]]; then
          FUNCTION_NAMES+=("${BASH_REMATCH[1]}")
        elif [[ "$line" =~ (function|class)[[:space:]]+([a-zA-Z0-9_]+) ]]; then
          FUNCTION_NAMES+=("${BASH_REMATCH[2]}")
        fi
      done <<< "$EXPORTS"
    fi
    ;;
    
  "py")
    # Extract function and class names from Python files
    if command -v grep &> /dev/null; then
      # Extract function definitions
      FUNCTIONS=$(grep -E '^def\s+[a-zA-Z0-9_]+\(' "$IMPLEMENTATION_FILE")
      
      # Extract class definitions
      CLASSES=$(grep -E '^class\s+[a-zA-Z0-9_]+(\(|:)' "$IMPLEMENTATION_FILE")
      
      # Extract function names
      while read -r line; do
        if [[ "$line" =~ def[[:space:]]+([a-zA-Z0-9_]+)\( ]]; then
          FUNCTION_NAMES+=("${BASH_REMATCH[1]}")
        fi
      done <<< "$FUNCTIONS"
      
      # Extract class names
      while read -r line; do
        if [[ "$line" =~ class[[:space:]]+([a-zA-Z0-9_]+)[\(\:] ]]; then
          FUNCTION_NAMES+=("${BASH_REMATCH[1]}")
        fi
      done <<< "$CLASSES"
    fi
    ;;
esac

# Generate test file content based on file type and extracted functions
case "$FILE_EXT" in
  "ts"|"tsx")
    # Generate TypeScript test file
    
    # If it's a React component
    if [[ "$IMPLEMENTATION_FILE" == *"/components/"* ]]; then
      cat > "$TEST_FILE" << EOF
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ${FILE_NAME_WITHOUT_EXT} } from '../${FILE_NAME}';

describe('${FILE_NAME_WITHOUT_EXT} Component', () => {
  test('renders correctly', () => {
    render(<${FILE_NAME_WITHOUT_EXT} />);
    // Add assertions based on component behavior
  });

  // Add more tests for component behavior
});
EOF
    else
      # For utility or other TypeScript files
      cat > "$TEST_FILE" << EOF
import { $(echo ${FUNCTION_NAMES[@]} | tr ' ' ', ') } from '../${FILE_NAME}';

describe('${FILE_NAME_WITHOUT_EXT}', () => {
$(for func in "${FUNCTION_NAMES[@]}"; do
  echo "  describe('${func}', () => {"
  echo "    test('should work correctly', () => {"
  echo "      // Arrange"
  echo "      // Act"
  echo "      // Assert"
  echo "      expect(true).toBe(true);"
  echo "    });"
  echo ""
  echo "    test('should handle edge cases', () => {"
  echo "      // Test edge cases like null inputs, empty arrays, etc."
  echo "      expect(true).toBe(true);"
  echo "    });"
  echo "  });"
  echo ""
done)
});
EOF
    fi
    ;;
    
  "js"|"jsx")
    # Generate JavaScript test file (similar to TypeScript but without types)
    
    # If it's a React component
    if [[ "$IMPLEMENTATION_FILE" == *"/components/"* ]]; then
      cat > "$TEST_FILE" << EOF
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ${FILE_NAME_WITHOUT_EXT} } from '../${FILE_NAME}';

describe('${FILE_NAME_WITHOUT_EXT} Component', () => {
  test('renders correctly', () => {
    render(<${FILE_NAME_WITHOUT_EXT} />);
    // Add assertions based on component behavior
  });

  // Add more tests for component behavior
});
EOF
    else
      # For utility or other JavaScript files
      cat > "$TEST_FILE" << EOF
import { $(echo ${FUNCTION_NAMES[@]} | tr ' ' ', ') } from '../${FILE_NAME}';

describe('${FILE_NAME_WITHOUT_EXT}', () => {
$(for func in "${FUNCTION_NAMES[@]}"; do
  echo "  describe('${func}', () => {"
  echo "    test('should work correctly', () => {"
  echo "      // Arrange"
  echo "      // Act"
  echo "      // Assert"
  echo "      expect(true).toBe(true);"
  echo "    });"
  echo ""
  echo "    test('should handle edge cases', () => {"
  echo "      // Test edge cases like null inputs, empty arrays, etc."
  echo "      expect(true).toBe(true);"
  echo "    });"
  echo "  });"
  echo ""
done)
});
EOF
    fi
    ;;
    
  "py")
    # Generate Python test file
    cat > "$TEST_FILE" << EOF
import pytest
from $(echo $IMPLEMENTATION_FILE | sed 's/\//./g' | sed 's/.py$//' | sed 's/^src\.//' | sed 's/^\.//' ) import $(echo ${FUNCTION_NAMES[@]} | tr ' ' ', ')

$(for func in "${FUNCTION_NAMES[@]}"; do
  if [[ "$func" =~ ^[A-Z] ]]; then
    # It's a class
    echo "class Test${func}:"
    echo "    def test_initialization(self):"
    echo "        # Arrange"
    echo "        # Act"
    echo "        instance = ${func}()"
    echo "        # Assert"
    echo "        assert instance is not None"
    echo ""
    echo "    def test_methods(self):"
    echo "        # Arrange"
    echo "        instance = ${func}()"
    echo "        # Act & Assert"
    echo "        # Add test for class methods"
    echo "        assert True"
    echo ""
  else
    # It's a function
    echo "def test_${func}_basic_functionality():"
    echo "    # Arrange"
    echo "    # Act"
    echo "    result = ${func}()"
    echo "    # Assert"
    echo "    assert result is not None"
    echo ""
    echo "def test_${func}_edge_cases():"
    echo "    # Test edge cases"
    echo "    # Example: empty inputs, None values, etc."
    echo "    assert True"
    echo ""
  fi
done)
EOF
    ;;
esac

# Set appropriate file permissions
chmod 644 "$TEST_FILE"

echo "✅ Test file created successfully: $TEST_FILE"
echo ""
echo "Next steps:"
echo "1. Edit the test file to add proper assertions"
echo "2. Run the tests with appropriate command"
case "$FILE_EXT" in
  "ts"|"tsx"|"js"|"jsx")
    echo "   npm test ${TEST_FILE}"
    ;;
  "py")
    echo "   pytest ${TEST_FILE}"
    ;;
esac
echo "3. Check test coverage and implement additional tests as needed" 