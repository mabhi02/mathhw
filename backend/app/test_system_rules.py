import logging
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import directly without using backend.app.core
from backend.app.core.system_rules.rules import SESATSRules
from backend.app.core.system_rules.prompts import SESATSPromptTemplate
from backend.app.core.system_rules.validation import QuestionValidator
from backend.app.core.system_rules.agent_integration import get_sesats_system_prompt_for_agent

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rules_loading():
    """Test loading SESATS rules from file"""
    rules = SESATSRules()
    result = rules.load_rules()
    assert result is not None
    assert "SESATS_Question_Writing_Guidelines" in result
    logger.info("Successfully loaded SESATS rules")
    
    guidelines = rules.get_guidelines()
    assert hasattr(guidelines, "item_structure")
    logger.info("Successfully parsed SESATS guidelines")
    
    example = rules.get_example()
    assert hasattr(example, "stem")
    logger.info("Successfully parsed example question")

def test_prompt_generation():
    """Test generating prompts with SESATS guidelines"""
    task_description = "Create a high-quality surgical question following SESATS guidelines."
    prompt = get_sesats_system_prompt_for_agent("question_generator", task_description=task_description)
    assert prompt is not None
    assert len(prompt) > 100
    assert "SESATS" in prompt
    assert task_description in prompt
    logger.info("Successfully generated prompt with SESATS guidelines")

def test_question_validation():
    """Test validating a question against SESATS guidelines"""
    # Create a valid question
    question = {
        "text": "A 65-year-old male with COPD presents with a 3cm peripheral right upper lobe mass. CT-guided biopsy confirms non-small cell lung cancer. The most appropriate surgical management is...",
        "options": [
            {"text": "Lobectomy", "isCorrect": True},
            {"text": "Pneumonectomy", "isCorrect": False},
            {"text": "Wedge resection", "isCorrect": False}
        ],
        "explanation": "Lobectomy is the gold standard surgical treatment for early-stage non-small cell lung cancer. Pneumonectomy is overly aggressive for this peripheral lesion. Wedge resection may be appropriate in patients with poor pulmonary function but offers inferior oncologic outcomes compared to lobectomy in patients who can tolerate it."
    }
    
    validator = QuestionValidator()
    result = validator.validate_question(question)
    assert result["valid"]
    assert result["score"] >= 90
    logger.info(f"Valid question validation score: {result['score']}")
    
    # Create an invalid question
    bad_question = {
        "text": "What is the treatment for lung cancer?", # Too short, no lead-in
        "options": [
            {"text": "Surgery", "isCorrect": True},
            {"text": "Radiation and surgery", "isCorrect": False}
        ], # Only 2 options
        "explanation": "Surgery is the standard first-line treatment." # Too short
    }
    
    result = validator.validate_question(bad_question)
    assert not result["valid"]
    assert result["score"] < 70
    logger.info(f"Invalid question validation score: {result['score']}")
    logger.info(f"Validation issues: {result['issues']}")

if __name__ == "__main__":
    logger.info("Running system rules tests...")
    
    try:
        test_rules_loading()
        test_prompt_generation()
        test_question_validation()
        logger.info("All tests passed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {e}") 