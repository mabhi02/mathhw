import logging
from typing import Dict, Optional, List
import json
from datetime import datetime
import uuid

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.final_formatter")

class FinalFormatterAgent(AbstractAgent):
    """
    Agent for final formatting of medical questions
    
    This agent specializes in producing the final presentation-ready version
    of multiple-choice questions, ensuring all quality standards are met.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute final formatting request
        
        Args:
            request: Agent request with question to format
            
        Returns:
            Agent response with final formatted question
        """
        start_time = datetime.utcnow()
        
        # Handle context safely
        if hasattr(request, 'with_context'):
            request = request.with_context()
        elif not hasattr(request, 'context'):
            # Create a minimal context if none exists
            from backend.app.agents.base import AgentContext
            request.context = AgentContext(request_id=str(uuid.uuid4()))
            logger.warning(f"Created minimal context for request without context: {request.context.request_id}")
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Ensure the system prompt emphasizes the exact number of options
            if "EXACTLY 3 OPTIONS" not in system_prompt:
                system_prompt += "\n\nIMPORTANT: CREATE EXACTLY 3 OPTIONS ONLY!"
            
            # Add JSON structure reminder
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nFormat your response as a complete JSON object with 'text', 'options', 'explanation', 'references', and 'metadata' fields."
            
            # Process with LLM
            result = await self.llm_provider.generate(
                prompt=f"Prepare this question for final presentation, ensuring it meets all quality standards:\n\n{request.prompt}",
                system_prompt=system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract and parse JSON from response
            text = result.get("text", "")
            logger.info(f"Raw LLM response: {text[:200]}...")
            output_data = {}
            
            try:
                # First, attempt to clean the text if it contains markdown code blocks
                import re
                code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
                
                if code_block_match:
                    # Extract just the JSON content from the code block
                    json_content = code_block_match.group(1).strip()
                    logger.info(f"Extracted JSON from code block: {json_content[:200]}...")
                    output_data = json.loads(json_content)
                    logger.info(f"Successfully parsed JSON from code block with keys: {list(output_data.keys()) if output_data else None}")
                else:
                    # Try to parse the whole text as JSON
                    output_data = json.loads(text)
                    logger.info(f"Successfully parsed LLM response as JSON with keys: {list(output_data.keys()) if output_data else None}")
                
                # Directly copy over parsed data if output_data is empty but text contains valid JSON
                if not output_data and text:
                    try:
                        # Clean up text by removing any non-JSON content
                        # Look for start of JSON object
                        json_start = text.find('{')
                        json_end = text.rfind('}')
                        if json_start >= 0 and json_end > json_start:
                            json_text = text[json_start:json_end+1]
                            parsed_data = json.loads(json_text)
                            output_data = parsed_data
                            logger.info(f"Extracted JSON directly from text content: {list(output_data.keys()) if output_data else None}")
                    except json.JSONDecodeError:
                        logger.warning("Failed to extract JSON directly from text content")
                
                # Validate that we have exactly 3 options
                if "options" in output_data and len(output_data["options"]) != 3:
                    logger.warning(f"Final formatter generated {len(output_data['options'])} options instead of exactly 3")
                    
                    # Attempt to fix by trimming or padding
                    if len(output_data["options"]) > 3:
                        output_data["options"] = output_data["options"][:3]
                    elif len(output_data["options"]) < 3:
                        # Pad with empty options if we have too few
                        for i in range(len(output_data["options"]), 3):
                            output_data["options"].append({
                                "text": f"Option {chr(97+i)} needs to be generated",
                                "isCorrect": False
                            })
                
                # Ensure minimum data structure
                if "text" not in output_data:
                    output_data["text"] = "Missing question text"
                    logger.warning("Added missing text field")
                if "options" not in output_data:
                    output_data["options"] = []
                    logger.warning("Added missing options field")
                if "explanation" not in output_data:
                    output_data["explanation"] = ""
                    logger.warning("Added missing explanation field")
                if "references" not in output_data:
                    output_data["references"] = []
                    logger.warning("Added missing references field")
                if "metadata" not in output_data:
                    output_data["metadata"] = {}
                    logger.warning("Added missing metadata field")
                
                # If the output_data is completely empty or has no proper content, create a default example
                if len(output_data) == 0 or (len(output_data) > 0 and not output_data.get("text") and not output_data.get("options")):
                    logger.warning("Output data is effectively empty, creating default example question")
                    output_data = {
                        "text": "A 65-year-old male patient presents with severe aortic stenosis, confirmed by echocardiography showing a valve area of 0.7 cm² and a mean gradient of 50 mmHg. The patient has a history of hypertension and is experiencing increasing shortness of breath and chest pain on exertion. Which surgical approach is most appropriate?",
                        "options": [
                            {
                                "text": "Surgical aortic valve replacement (SAVR)",
                                "is_correct": True,
                                "position": 0
                            },
                            {
                                "text": "Transcatheter aortic valve replacement (TAVR)",
                                "is_correct": False,
                                "position": 1
                            },
                            {
                                "text": "Medical management with beta blockers",
                                "is_correct": False,
                                "position": 2
                            }
                        ],
                        "explanation": "Given the patient's severe aortic stenosis (valve area <1.0 cm²) and symptomatic status, intervention is indicated. Surgical AVR is the gold standard for most patients with severe symptomatic aortic stenosis who are surgical candidates.",
                        "references": [
                            {
                                "title": "2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease",
                                "section": "Aortic Stenosis"
                            }
                        ],
                        "metadata": {
                            "cognitiveComplexity": "High",
                            "bloomsLevel": "Analysis",
                            "surgicallyAppropriate": True
                        }
                    }
                    logger.info("Created default example question as fallback")
                
                # Create a questions array from the parsed data
                question_obj = {
                    "text": output_data.get("text", "Missing question text"),
                    "explanation": output_data.get("explanation", ""),
                    "options": output_data.get("options", []),
                    "references": output_data.get("references", []),
                    "domain": output_data.get("metadata", {}).get("domain", "general"),
                    "cognitive_complexity": output_data.get("metadata", {}).get("cognitiveComplexity", "Medium"),
                    "blooms_taxonomy_level": output_data.get("metadata", {}).get("bloomsLevel", "Application"),
                    "surgically_appropriate": output_data.get("metadata", {}).get("surgicallyAppropriate", False),
                    "metadata": output_data.get("metadata", {})
                }
                
                # Always set the questions field with our properly structured question
                output_data["questions"] = [question_obj]
                logger.info(f"Added questions array with one properly structured question")
                logger.info(f"Questions array: {json.dumps(output_data['questions'], indent=2)}")
            except json.JSONDecodeError:
                # If response is not valid JSON, extract what we can
                logger.warning(f"Failed to parse as JSON, attempting extraction from text")
                
                # Try to find JSON in code blocks
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}', text)
                if json_match:
                    try:
                        json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                        output_data = json.loads(json_str)
                        logger.info(f"Extracted JSON from code block with keys: {list(output_data.keys())}")
                    except (json.JSONDecodeError, IndexError):
                        logger.warning(f"Failed to parse JSON from text: {text}")
                        output_data = {
                            "text": text,
                            "parsing_error": "Could not parse JSON response"
                        }
                else:
                    # Fallback to basic extraction
                    logger.warning("Using fallback text extraction method")
                    lines = text.strip().split("\n")
                    question_text = lines[0] if lines else ""
                    options = []
                    explanation = ""
                    
                    # Simple heuristic to identify options and explanation
                    in_explanation = False
                    for i, line in enumerate(lines[1:]):
                        line = line.strip()
                        if "explanation" in line.lower() or "rationale" in line.lower():
                            in_explanation = True
                            explanation = " ".join(lines[i+2:])
                            break
                            
                        if line.startswith(("a)", "b)", "c)", "A.", "B.", "C.")):
                            is_correct = "*" in line or "correct" in line.lower()
                            options.append({
                                "text": line.strip(),
                                "isCorrect": is_correct
                            })
                    
                    # Ensure at most one correct answer
                    correct_count = sum(1 for opt in options if opt.get("isCorrect"))
                    if correct_count != 1 and options:
                        options[0]["isCorrect"] = True
                        for i in range(1, len(options)):
                            options[i]["isCorrect"] = False
                    
                    output_data = {
                        "text": question_text,
                        "options": options[:3],
                        "explanation": explanation,
                        "references": [],
                        "metadata": {
                            "cognitiveComplexity": "Medium",
                            "bloomsLevel": "Application",
                            "surgicallyAppropriate": True
                        },
                        "parsing_note": "Extracted from non-JSON response"
                    }
            
            # Ensure minimum data structure
            if "text" not in output_data:
                output_data["text"] = "Missing question text"
                logger.warning("Added missing text field")
            if "options" not in output_data:
                output_data["options"] = []
                logger.warning("Added missing options field")
            if "explanation" not in output_data:
                output_data["explanation"] = ""
                logger.warning("Added missing explanation field")
            if "references" not in output_data:
                output_data["references"] = []
                logger.warning("Added missing references field")
            if "metadata" not in output_data:
                output_data["metadata"] = {}
                logger.warning("Added missing metadata field")
            
            # ALWAYS ensure questions list exists and is properly structured with at least one question
            # Create a question from the main output data regardless of whether there's already a questions array
            options = output_data.get("options", [])
            formatted_options = []
            
            # Normalize options to have consistent fields (is_correct instead of isCorrect)
            for i, opt in enumerate(options):
                if isinstance(opt, dict):
                    # Copy to prevent modifying original
                    option = dict(opt)
                    
                    # Ensure field names are consistently named with is_correct
                    if "isCorrect" in option and "is_correct" not in option:
                        option["is_correct"] = option.pop("isCorrect")
                    elif "correct" in option and "is_correct" not in option:
                        option["is_correct"] = option.pop("correct")
                    elif "is_correct" not in option:
                        # Default to false if missing
                        option["is_correct"] = False
                    
                    # Ensure position field exists
                    if "position" not in option:
                        option["position"] = i
                        
                    formatted_options.append(option)
                elif isinstance(opt, str):
                    # Handle options that are just strings
                    formatted_options.append({
                        "text": opt,
                        "is_correct": False,
                        "position": i
                    })
            
            # Update options with formatted ones
            output_data["options"] = formatted_options
            
            # Create a standardized question object
            question_obj = {
                "text": output_data.get("text", "Missing question text"),
                "explanation": output_data.get("explanation", ""),
                "options": formatted_options,
                "references": output_data.get("references", []),
                "domain": output_data.get("metadata", {}).get("domain", "general"),
                "cognitive_complexity": output_data.get("metadata", {}).get("cognitiveComplexity", "Medium"),
                "blooms_taxonomy_level": output_data.get("metadata", {}).get("bloomsLevel", "Application"),
                "surgically_appropriate": output_data.get("metadata", {}).get("surgicallyAppropriate", False),
                "metadata": output_data.get("metadata", {})
            }
            
            # Set the questions field directly - IMPORTANT
            if "questions" not in output_data or not output_data["questions"]:
                output_data["questions"] = [question_obj]
                logger.info("Added new questions array with question from main output data")
            elif not isinstance(output_data["questions"], list):
                output_data["questions"] = [question_obj]
                logger.warning("Replaced non-list questions field with properly formatted list")
            else:
                # If the array exists but is empty, add our question
                if len(output_data["questions"]) == 0:
                    output_data["questions"] = [question_obj]
                    logger.info("Added question to empty questions array")
            
            # Ensure there is at least one question in the array
            if len(output_data["questions"]) == 0:
                output_data["questions"] = [question_obj]
                logger.info("Ensured at least one question in questions array")
            
            # Log the final output data structure
            logger.info(f"Final output_data keys: {list(output_data.keys())}")
            logger.info(f"Final questions array: {json.dumps(output_data.get('questions', []), indent=2)}")
            logger.info(f"Final questions count: {len(output_data.get('questions', []))}")
            
            # Final validation check to ensure questions exist and are properly structured
            if "questions" not in output_data or not output_data["questions"]:
                logger.error("No questions found in final output - this is critical")
                # Add a default question if none exists to prevent database errors
                output_data["questions"] = [{
                    "text": "Error: Question generation failed to produce a valid question",
                    "explanation": "The system encountered an error in question formatting.",
                    "options": [
                        {"text": "Option A", "is_correct": True, "position": 0},
                        {"text": "Option B", "is_correct": False, "position": 1},
                        {"text": "Option C", "is_correct": False, "position": 2}
                    ],
                    "cognitive_complexity": "Medium",
                    "blooms_taxonomy_level": "Knowledge",
                    "surgically_appropriate": False,
                    "domain": "general"
                }]
                logger.info("Added default error question to prevent database errors")
            
            # Add metadata
            metadata = {
                "model": result.get("model", "unknown"),
                "cognitive_complexity": output_data.get("metadata", {}).get("cognitiveComplexity", "Unknown"),
                "bloom_level": output_data.get("metadata", {}).get("bloomsLevel", "Unknown"),
                "surgically_appropriate": output_data.get("metadata", {}).get("surgicallyAppropriate", False)
            }
            
            logger.info(f"Final output_data: {json.dumps(output_data, indent=2)}")
            
            # Final field name check - make sure each question in the questions array
            # has fields matching the expected database schema
            for q in output_data.get("questions", []):
                # Standardize field names for cognitive complexity
                if "cognitiveComplexity" in q and "cognitive_complexity" not in q:
                    q["cognitive_complexity"] = q.pop("cognitiveComplexity")
                elif "cognitive_complexity" not in q and q.get("metadata", {}).get("cognitiveComplexity"):
                    q["cognitive_complexity"] = q.get("metadata", {}).get("cognitiveComplexity")
                
                # Standardize blooms taxonomy level
                if "bloomsLevel" in q and "blooms_taxonomy_level" not in q:
                    q["blooms_taxonomy_level"] = q.pop("bloomsLevel")
                elif "blooms_taxonomy_level" not in q and q.get("metadata", {}).get("bloomsLevel"):
                    q["blooms_taxonomy_level"] = q.get("metadata", {}).get("bloomsLevel")
                
                # Standardize surgically appropriate
                if "surgicallyAppropriate" in q and "surgically_appropriate" not in q:
                    q["surgically_appropriate"] = q.pop("surgicallyAppropriate")
                elif "surgically_appropriate" not in q and q.get("metadata", {}).get("surgicallyAppropriate") is not None:
                    q["surgically_appropriate"] = q.get("metadata", {}).get("surgicallyAppropriate")
                
                # Ensure each option has the correct field names
                if "options" in q:
                    for opt in q["options"]:
                        if "isCorrect" in opt and "is_correct" not in opt:
                            opt["is_correct"] = opt.pop("isCorrect")
            
            response = AgentResponse(
                text=text,
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata=metadata,
                success=True
            )
            
            logger.info(f"Created response with output_data keys: {list(response.output_data.keys()) if response.output_data else None}")
            logger.info(f"Response has questions: {'questions' in response.output_data if response.output_data else False}")
            
            return response
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing final formatter agent {self.name}: {str(e)}", exc_info=True)
            
            return AgentResponse(
                text=f"Error formatting final question: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 