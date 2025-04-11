from typing import Dict, Any, List, Optional, Union
import logging
import yaml
import os
from pydantic import BaseModel, Field

from backend.app.config import get_settings

# Setup logger
logger = logging.getLogger("app.core.system_rules")

class ItemStructure(BaseModel):
    """Structure for SESATS question items"""
    terminology: Dict[str, str] = Field(default_factory=dict)
    components: List[str] = Field(default_factory=list)
    stem: Dict[str, Any] = Field(default_factory=dict)

class ResponseOptions(BaseModel):
    """Rules for response options in SESATS questions"""
    structure: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    formatting_guidelines: List[str] = Field(default_factory=list)
    trick_avoidance: List[str] = Field(default_factory=list)

class DifficultyLevel(BaseModel):
    """Rules for difficulty levels in SESATS questions"""
    principles: List[str] = Field(default_factory=list)

class SESATSGuidelines(BaseModel):
    """SESATS question writing guidelines"""
    overview: Dict[str, Any] = Field(default_factory=dict)
    item_structure: ItemStructure = Field(default_factory=ItemStructure)
    response_options: ResponseOptions = Field(default_factory=ResponseOptions)
    difficulty_level: DifficultyLevel = Field(default_factory=DifficultyLevel)
    critiques: Dict[str, Any] = Field(default_factory=dict)
    references: Dict[str, Any] = Field(default_factory=dict)
    grammar_and_style: Dict[str, Any] = Field(default_factory=dict)
    exam_policy: Dict[str, Any] = Field(default_factory=dict)

class ExampleQuestion(BaseModel):
    """Example question for reference"""
    stem: str
    answer_options: List[str]
    critique: str
    reference: List[str] = Field(default_factory=list)

class SystemRules:
    """
    Base class for system rules
    
    Handles loading and parsing of rule files.
    """
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize system rules
        
        Args:
            rules_file: Path to rules file, defaults to settings
        """
        settings = get_settings()
        self.rules_file = rules_file or os.path.join(
            settings.CONFIG_DIR, 
            settings.QUESTION_RULES_FILE
        )
        self._rules = {}
        self._loaded = False
        
    def load_rules(self) -> Dict[str, Any]:
        """
        Load rules from file
        
        Returns:
            Dictionary of rules
        """
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
    
    def get_rule(self, rule_path: str) -> Any:
        """
        Get a specific rule by path
        
        Args:
            rule_path: Dot-separated path to rule (e.g., "section.subsection.rule")
            
        Returns:
            Rule value or None if not found
        """
        if not self._loaded:
            self.load_rules()
            
        parts = rule_path.split('.')
        value = self._rules
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                logger.warning(f"Rule not found: {rule_path}")
                return None
                
        return value
    
    def get_all_rules(self) -> Dict[str, Any]:
        """
        Get all rules
        
        Returns:
            Dictionary of all rules
        """
        if not self._loaded:
            self.load_rules()
            
        return self._rules


class SESATSRules(SystemRules):
    """
    Rules for SESATS question generation
    
    Provides structured access to SESATS guidelines.
    """
    
    def __init__(self, rules_file: Optional[str] = None):
        """
        Initialize SESATS rules
        
        Args:
            rules_file: Path to rules file, defaults to settings
        """
        super().__init__(rules_file)
        self._guidelines = None
        self._example = None
        
    def get_guidelines(self) -> SESATSGuidelines:
        """
        Get SESATS guidelines
        
        Returns:
            SESATS guidelines model
        """
        if not self._loaded:
            self.load_rules()
            
        if not self._guidelines:
            guidelines_dict = self._rules.get('SESATS_Question_Writing_Guidelines', {})
            self._guidelines = SESATSGuidelines(**guidelines_dict)
            
        return self._guidelines
    
    def get_example(self) -> ExampleQuestion:
        """
        Get example question
        
        Returns:
            Example question model
        """
        if not self._loaded:
            self.load_rules()
            
        if not self._example:
            example_dict = self._rules.get('example', {}).get('question', {})
            self._example = ExampleQuestion(**example_dict)
            
        return self._example
    
    def get_stem_guidelines(self) -> Dict[str, Any]:
        """
        Get stem writing guidelines
        
        Returns:
            Stem guidelines dictionary
        """
        guidelines = self.get_guidelines()
        return guidelines.item_structure.stem
    
    def get_response_guidelines(self) -> ResponseOptions:
        """
        Get response options guidelines
        
        Returns:
            Response options guidelines
        """
        guidelines = self.get_guidelines()
        return guidelines.response_options
    
    def get_lead_in_examples(self) -> List[str]:
        """
        Get lead-in examples for stems
        
        Returns:
            List of lead-in examples
        """
        guidelines = self.get_guidelines()
        return guidelines.item_structure.stem.get('lead_in_examples', [])
    
    def get_things_to_avoid(self) -> List[str]:
        """
        Get things to avoid in stems
        
        Returns:
            List of things to avoid
        """
        guidelines = self.get_guidelines()
        return guidelines.item_structure.stem.get('avoid', []) 