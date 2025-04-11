#!/usr/bin/env python
import json
import re
import asyncio
from backend.app.agents.implementations.final_formatter import FinalFormatterAgent
from backend.app.agents.base import AgentRequest, AgentContext

def parse_json_from_markdown(text):
    """Parse JSON from a markdown code block or plain text"""
    try:
        # First, attempt to clean the text if it contains markdown code blocks
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        
        if code_block_match:
            # Extract just the JSON content from the code block
            json_content = code_block_match.group(1).strip()
            print(f"Extracted JSON from code block: {json_content[:200]}...")
            parsed_data = json.loads(json_content)
            print(f"Successfully parsed JSON from code block with keys: {list(parsed_data.keys())}")
            return parsed_data
        else:
            # Try to parse the whole text as JSON
            parsed_data = json.loads(text)
            print(f"Successfully parsed plain text as JSON with keys: {list(parsed_data.keys())}")
            return parsed_data
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None

# Test with a JSON string inside a markdown code block
test_json = '''```json
{
  "text": "This is a test question",
  "options": [
    {
      "text": "Option A",
      "isCorrect": true
    },
    {
      "text": "Option B",
      "isCorrect": false
    },
    {
      "text": "Option C",
      "isCorrect": false
    }
  ],
  "explanation": "This is a test explanation",
  "references": [],
  "metadata": {
    "cognitiveComplexity": "Medium",
    "bloomsLevel": "Application"
  }
}
```'''

async def test_formatter():
    # Create the final formatter agent
    agent = FinalFormatterAgent(
        agent_id="test-formatter",
        name="Test Formatter",
        description="Test formatter agent",
        instructions="Test instructions"
    )
    
    # Create a request
    request = AgentRequest(
        prompt=test_json,
        context=AgentContext()
    )
    
    # Execute the agent
    response = await agent.execute(request)
    
    # Print the result
    print("Response success:", response.success)
    print("Response text length:", len(response.text))
    print("Response has output_data:", response.output_data is not None)
    print("Response output_data keys:", list(response.output_data.keys()) if response.output_data else None)
    print("Response has questions:", "questions" in response.output_data if response.output_data else False)
    print("Questions count:", len(response.output_data.get("questions", [])) if response.output_data else 0)
    
    if response.output_data and "questions" in response.output_data:
        questions = response.output_data["questions"]
        print("\nQuestions:")
        print(json.dumps(questions, indent=2))

# Run our test
if __name__ == "__main__":
    # Parse JSON from markdown
    result = parse_json_from_markdown(test_json)
    print("Parsed result:", result)
    
    # Now create a questions array from this
    if result:
        question_obj = {
            "text": result.get("text", "Missing question text"),
            "explanation": result.get("explanation", ""),
            "options": result.get("options", []),
            "references": result.get("references", []),
            "domain": result.get("metadata", {}).get("domain", "general"),
            "metadata": result.get("metadata", {})
        }
        
        result["questions"] = [question_obj]
        print("Added questions array:", result["questions"])
    
    # Test the formatter agent
    print("\nTesting formatter agent...")
    asyncio.run(test_formatter()) 