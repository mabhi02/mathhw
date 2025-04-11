from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import re

from backend.app.core.system_rules.rules import SESATSRules

# Setup logger
logger = logging.getLogger("app.core.system_rules.validation")

class QuestionValidator:
    """
    Validator for questions against SESATS guidelines
    
    Checks questions for compliance with SESATS guidelines.
    """
    
    def __init__(self, rules: Optional[SESATSRules] = None):
        """
        Initialize question validator
        
        Args:
            rules: Optional SESATS rules
        """
        self.rules = rules or SESATSRules()
        
    def validate_stem(self, stem: str) -> Tuple[bool, List[str]]:
        """
        Validate stem against SESATS guidelines
        
        Args:
            stem: Question stem to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check length
        if len(stem.split()) < 10:
            issues.append("Stem is too short. It should be a detailed clinical vignette.")
            
        # Check for things to avoid
        things_to_avoid = self.rules.get_things_to_avoid()
        for thing in things_to_avoid:
            # Create regex pattern to match the thing to avoid
            pattern = re.compile(re.escape(thing.lower()))
            if pattern.search(stem.lower()):
                issues.append(f"Stem contains something to avoid: {thing}")
                
        # Check for lead-in
        lead_ins = self.rules.get_lead_in_examples()
        has_lead_in = False
        
        for lead_in in lead_ins:
            if lead_in.lower() in stem.lower():
                has_lead_in = True
                break
                
        if not has_lead_in:
            issues.append("Stem does not contain a proper lead-in. Consider adding one of the recommended lead-ins.")
            
        # Check if it's a complete sentence ending with punctuation
        if not stem.strip().endswith(('?', '.', ':', '...')):
            issues.append("Stem should end with proper punctuation (?, ., :, ...).")
            
        return len(issues) == 0, issues
    
    def validate_options(self, options: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate response options against SESATS guidelines
        
        Args:
            options: List of response options in the format [{"text": "Option text", "isCorrect": True/False}, ...]
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check number of options
        if len(options) != 3:
            issues.append(f"There should be exactly 3 options, found {len(options)}.")
            
        # Check for one correct answer
        correct_count = sum(1 for opt in options if opt.get('isCorrect'))
        if correct_count != 1:
            issues.append(f"There should be exactly 1 correct option, found {correct_count}.")
            
        # Check option lengths (should be relatively similar)
        option_lengths = [len(opt.get('text', '')) for opt in options]
        avg_length = sum(option_lengths) / len(option_lengths) if option_lengths else 0
        
        for i, length in enumerate(option_lengths):
            if length < avg_length * 0.5 or length > avg_length * 2:
                issues.append(f"Option {i+1} has an unusual length compared to others. Options should be of similar length.")
                
        # Check for homogeneity
        option_texts = [opt.get('text', '').lower() for opt in options]
        
        # Check for grammatical parallelism
        first_words = [text.split()[0] if text and ' ' in text else '' for text in option_texts]
        if len(set(first_words)) > 1:
            issues.append("Options should have grammatical parallelism. Consider starting all options with similar words.")
            
        # Check for absolute words ("always", "never", "all", "none")
        absolute_words = ["always", "never", "all", "none", "every", "only"]
        for i, text in enumerate(option_texts):
            for word in absolute_words:
                if f" {word} " in f" {text} ":
                    issues.append(f"Option {i+1} contains the absolute word '{word}', which should be avoided.")
        
        return len(issues) == 0, issues
    
    def validate_explanation(self, explanation: str) -> Tuple[bool, List[str]]:
        """
        Validate explanation against SESATS guidelines
        
        Args:
            explanation: Explanation to validate
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check length
        if len(explanation.split()) < 50:
            issues.append("Explanation is too short. It should thoroughly explain why the correct answer is correct and why the distractors are incorrect.")
            
        # Check if it mentions "correct" or similar
        if not any(word in explanation.lower() for word in ["correct", "right", "appropriate", "best"]):
            issues.append("Explanation should explicitly mention why the correct answer is correct.")
            
        # Check if it mentions "incorrect" or similar
        if not any(word in explanation.lower() for word in ["incorrect", "wrong", "inappropriate", "not", "less"]):
            issues.append("Explanation should explain why the incorrect options are not the best choices.")
            
        return len(issues) == 0, issues
    
    def validate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete question against SESATS guidelines
        
        Args:
            question: Question dictionary with "text" (stem), "options", "explanation", etc.
            
        Returns:
            Validation result with issues
        """
        result = {
            "valid": True,
            "issues": {
                "stem": [],
                "options": [],
                "explanation": [],
                "general": []
            },
            "score": 100  # Start with perfect score
        }
        
        # Validate stem
        stem_valid, stem_issues = self.validate_stem(question.get('text', ''))
        if not stem_valid:
            result["valid"] = False
            result["issues"]["stem"] = stem_issues
            result["score"] -= 10 * len(stem_issues)  # Deduct 10 points per issue
            
        # Validate options
        options_valid, option_issues = self.validate_options(question.get('options', []))
        if not options_valid:
            result["valid"] = False
            result["issues"]["options"] = option_issues
            result["score"] -= 15 * len(option_issues)  # Deduct 15 points per issue
            
        # Validate explanation
        explanation_valid, explanation_issues = self.validate_explanation(question.get('explanation', ''))
        if not explanation_valid:
            result["valid"] = False
            result["issues"]["explanation"] = explanation_issues
            result["score"] -= 10 * len(explanation_issues)  # Deduct 10 points per issue
            
        # Ensure score doesn't go negative
        result["score"] = max(0, result["score"])
        
        return result
    
    
def validate_against_sesats(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a question against SESATS guidelines
    
    Args:
        question: Question dictionary with "text", "options", "explanation"
        
    Returns:
        Validation result
    """
    validator = QuestionValidator()
    return validator.validate_question(question) 