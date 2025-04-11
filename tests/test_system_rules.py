import logging
import os
import yaml
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simplified models
class ItemStructure(BaseModel):
    """Structure for SESATS question items"""
    terminology: Dict[str, str] = Field(default_factory=dict)
    components: List[str] = Field(default_factory=list)
    stem: Dict[str, Any] = Field(default_factory=dict)

class SESATSGuidelines(BaseModel):
    """SESATS question writing guidelines"""
    overview: Dict[str, Any] = Field(default_factory=dict)
    item_structure: Dict[str, Any] = Field(default_factory=dict)
    
# Simplified rules loader
class SESATSRules:
    def __init__(self, rules_file: str = "config/question_rules.yml"):
        self.rules_file = rules_file
        self._rules = {}
        self._loaded = False
        
    def load_rules(self) -> Dict[str, Any]:
        if self._loaded:
            return self._rules
            
        try:
            with open(self.rules_file, 'r') as f:
                self._rules = yaml.safe_load(f)
            
            self._loaded = True
            logger.info(f"Loaded rules from {self.rules_file}")
            return self._rules
            
        except Exception as e:
            logger.error(f"Error loading rules from {self.rules_file}: {e}")
            return {}
    
    def get_guidelines(self) -> Dict[str, Any]:
        if not self._loaded:
            self.load_rules()
        return self._rules.get('SESATS_Question_Writing_Guidelines', {})
    
    def get_example(self) -> Dict[str, Any]:
        if not self._loaded:
            self.load_rules()
        return self._rules.get('example', {}).get('question', {})

# Simplified validator
class QuestionValidator:
    def __init__(self, rules):
        self.rules = rules
        
    def validate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        result = {
            "valid": True,
            "issues": {
                "stem": [],
                "options": [],
                "explanation": []
            },
            "score": 100
        }
        
        # Validate stem
        stem = question.get('text', '')
        if len(stem.split()) < 10:
            result["valid"] = False
            result["issues"]["stem"].append("Stem is too short")
            result["score"] -= 10
            
        # Validate options
        options = question.get('options', [])
        if len(options) != 3:
            result["valid"] = False
            result["issues"]["options"].append(f"Expected 3 options, found {len(options)}")
            result["score"] -= 15
            
        # Validate explanation
        explanation = question.get('explanation', '')
        if len(explanation.split()) < 50:
            result["valid"] = False
            result["issues"]["explanation"].append("Explanation is too short")
            result["score"] -= 10
            
        # Ensure score doesn't go negative
        result["score"] = max(0, result["score"])
        
        return result

def test_rules_loading():
    """Test loading SESATS rules from file"""
    rules = SESATSRules()
    result = rules.load_rules()
    assert result is not None
    assert "SESATS_Question_Writing_Guidelines" in result
    logger.info("Successfully loaded SESATS rules")
    
    guidelines = rules.get_guidelines()
    assert "item_structure" in guidelines
    logger.info("Successfully parsed SESATS guidelines")
    
    example = rules.get_example()
    assert "stem" in example
    logger.info("Successfully parsed example question")

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
    
    rules = SESATSRules()
    validator = QuestionValidator(rules)
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
        test_question_validation()
        logger.info("All tests passed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {e}") 