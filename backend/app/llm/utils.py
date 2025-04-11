"""
Utility functions for working with LLM responses.

This module provides helper functions for processing and extracting
structured data from LLM responses.
"""
import re
import json
import logging
from typing import Any, Dict, List, Optional, Union

# Configure logging
logger = logging.getLogger(__name__)

def extract_json_from_text(text: Union[str, Dict, List, Any]) -> Any:
    """
    Extract JSON from text that might be surrounded by other text.
    
    This function handles various formats of text that might contain JSON,
    including code blocks, direct JSON objects, and more. It also handles
    cases where the input is already a parsed Python object.
    
    Args:
        text: The text or object to extract JSON from
        
    Returns:
        The extracted JSON as a Python object, or an empty dict if extraction fails
    """
    try:
        # If already a dict or list, return as is
        if isinstance(text, (dict, list)):
            return text
            
        # For text outputs, try to extract JSON
        # First, check for code blocks with ```json
        code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})```', text, re.DOTALL)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                # Try to clean the JSON
                json_str = code_block_match.group(1)
                json_str = re.sub(r'//.*?\n', '\n', json_str)  # Remove comments
                return json.loads(json_str)
        
        # Look for code blocks with arrays
        array_block_match = re.search(r'```(?:json)?\s*(\[.*?\])```', text, re.DOTALL)
        if array_block_match:
            try:
                return json.loads(array_block_match.group(1))
            except json.JSONDecodeError:
                # Try to clean the JSON
                json_str = array_block_match.group(1)
                json_str = re.sub(r'//.*?\n', '\n', json_str)  # Remove comments
                return json.loads(json_str)
        
        # If no code block, look for any JSON object
        json_match = re.search(r'(\{.*\})', text.replace('\n', ' '), re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                # Try to clean the JSON
                json_str = json_match.group(1)
                json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)  # Remove comments
                return json.loads(json_str)
        
        # Look for JSON arrays
        array_match = re.search(r'(\[.*\])', text.replace('\n', ' '), re.DOTALL)
        if array_match:
            try:
                return json.loads(array_match.group(1))
            except json.JSONDecodeError:
                # Try to clean the JSON
                json_str = array_match.group(1)
                json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)  # Remove comments
                return json.loads(json_str)
        
        # If text is already valid JSON, parse it directly
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        logger.warning(f"Could not extract JSON from text: {text[:100]}...")
        return {}
    except Exception as e:
        logger.error(f"Error extracting JSON: {e}")
        logger.error(f"Text was: {text[:200]}...")
        return {} 