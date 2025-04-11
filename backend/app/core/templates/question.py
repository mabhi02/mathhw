"""
Question templates for SESATS format
"""
from typing import Dict, Any, List, Optional, Union
import logging
import os
import json
from pathlib import Path

from backend.app.core.templates.base import Template, TemplateRenderer
from backend.app.core.system_rules.rules import SESATSRules
from backend.app.config import get_settings

# Setup logger
logger = logging.getLogger("app.core.templates.question")

class QuestionTemplate(Template):
    """
    Template for SESATS question format
    
    Extends base template with SESATS-specific functionality.
    """
    
    # Template types based on SESATS stem format
    TEMPLATE_TYPES = {
        "clinical_scenario": "Clinical scenario with application of knowledge",
        "diagnostic": "Diagnostic reasoning question with clinical findings",
        "management": "Management decision question with treatment options",
        "technical": "Technical procedure question with surgical details",
        "complication": "Complication management question",
        "general": "General knowledge application question"
    }
    
    def __init__(self, 
                 template_text: str, 
                 template_id: Optional[str] = None,
                 template_type: str = "clinical_scenario",
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize question template
        
        Args:
            template_text: Raw template text with Jinja2 syntax
            template_id: Optional identifier for this template
            template_type: Type of question template
            metadata: Additional metadata for the template
        """
        super().__init__(template_text, template_id)
        self.template_type = template_type
        self.metadata = metadata or {}
        self.sesats_rules = SESATSRules()
    
    def render_with_guidelines(self, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Render the question template with SESATS guidelines
        
        Args:
            variables: Variables for template rendering
            
        Returns:
            Dictionary with rendered question components
        """
        variables = variables or {}
        
        # Add SESATS guidelines to variables if not already present
        if "sesats_guidelines" not in variables:
            guidelines = self.sesats_rules.get_guidelines()
            variables["sesats_guidelines"] = guidelines.dict()
        
        # Add example formats if not present
        if "lead_in_examples" not in variables:
            variables["lead_in_examples"] = self.sesats_rules.get_lead_in_examples()
        
        # Add things to avoid if not present
        if "things_to_avoid" not in variables:
            variables["things_to_avoid"] = self.sesats_rules.get_things_to_avoid()
        
        # Render the template
        rendered_text = self.render(variables)
        
        # Try to parse into components if JSON
        try:
            result = json.loads(rendered_text)
            # Ensure it has the required components
            if isinstance(result, dict):
                return result
        except Exception:
            # Not JSON or invalid format
            pass
        
        # If not parseable as JSON, return as stem
        return {"stem": rendered_text}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary representation
        
        Returns:
            Dictionary with template data
        """
        data = super().to_dict()
        data.update({
            "template_type": self.template_type,
            "metadata": self.metadata
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestionTemplate':
        """
        Create template from dictionary
        
        Args:
            data: Dictionary with template data
            
        Returns:
            QuestionTemplate instance
        """
        return cls(
            template_text=data.get("template_text", ""),
            template_id=data.get("template_id"),
            template_type=data.get("template_type", "clinical_scenario"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'QuestionTemplate':
        """
        Load template from file
        
        Args:
            file_path: Path to template file
            
        Returns:
            QuestionTemplate instance
        """
        try:
            file_path = Path(file_path)
            template_id = file_path.stem
            
            # Try to load as JSON first to get metadata
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "template_text" in data:
                        return cls.from_dict(data)
            except json.JSONDecodeError:
                pass
            
            # If not JSON, load as raw template text
            with open(file_path, 'r') as f:
                template_text = f.read()
            
            # Try to determine template type from filename
            template_type = "clinical_scenario"
            for t_type in cls.TEMPLATE_TYPES:
                if t_type in template_id:
                    template_type = t_type
                    break
            
            return cls(
                template_text=template_text, 
                template_id=template_id,
                template_type=template_type
            )
        except Exception as e:
            logger.error(f"Error loading template from {file_path}: {e}")
            return cls(template_text="", template_id="error")
    
    def save_to_file(self, file_path: Union[str, Path], include_metadata: bool = True) -> bool:
        """
        Save template to file
        
        Args:
            file_path: Path to save template
            include_metadata: Whether to include metadata (saved as JSON)
            
        Returns:
            True if successful
        """
        try:
            file_path = Path(file_path)
            
            if include_metadata:
                # Save as JSON with metadata
                data = self.to_dict()
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                # Save as raw template text
                with open(file_path, 'w') as f:
                    f.write(self.template_text)
            
            return True
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {e}")
            return False


class QuestionTemplateLoader(TemplateRenderer):
    """
    Specialized loader for question templates
    
    This class provides functionality to load and manage SESATS question templates.
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize question template loader
        
        Args:
            template_dir: Directory containing templates, defaults to settings/templates/question
        """
        settings = get_settings()
        template_dir = template_dir or os.path.join(settings.TEMPLATE_PATH, "question")
        super().__init__(template_dir)
        
        # Ensure the template directory exists
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Load built-in templates
        self._load_builtin_templates()
    
    def _load_builtin_templates(self):
        """Load built-in templates if no templates exist"""
        if not self.list_templates():
            self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default question templates"""
        # Clinical scenario template
        clinical_template = QuestionTemplate(
            template_text="""
{# Clinical Scenario Template #}
{# This template creates a clinical scenario question following SESATS guidelines #}
{
    "stem": "A {{ patient_age }}-year-old {{ patient_gender }} presents with {{ symptom_description }}. {{ additional_history }} On examination, {{ examination_findings }}. {{ test_results_if_applicable }}\n\n{{ lead_in_phrase }}",
    
    "answer_options": [
        {"text": "{{ option_a_text }}", "isCorrect": {{ option_a_correct }}},
        {"text": "{{ option_b_text }}", "isCorrect": {{ option_b_correct }}},
        {"text": "{{ option_c_text }}", "isCorrect": {{ option_c_correct }}}
    ],
    
    "explanation": "{{ explanation_text }}",
    
    "references": [
        {"title": "{{ reference_title }}", "section": "{{ reference_section }}"}
    ]
}
""",
            template_id="clinical_scenario",
            template_type="clinical_scenario",
            metadata={
                "description": "Template for clinical scenario questions",
                "required_variables": [
                    "patient_age", "patient_gender", "symptom_description", 
                    "examination_findings", "lead_in_phrase", 
                    "option_a_text", "option_a_correct", 
                    "option_b_text", "option_b_correct", 
                    "option_c_text", "option_c_correct", 
                    "explanation_text", "reference_title", "reference_section"
                ],
                "optional_variables": [
                    "additional_history", "test_results_if_applicable"
                ]
            }
        )
        
        # Management decision template
        management_template = QuestionTemplate(
            template_text="""
{# Management Decision Template #}
{# This template creates a management decision question following SESATS guidelines #}
{
    "stem": "{% if emergency_situation %}An urgent consultation is requested for {% else %}You are asked to evaluate {% endif %}a {{ patient_age }}-year-old {{ patient_gender }} with {{ diagnosis }}. {{ clinical_context }}.\n\n{{ lead_in_phrase }}",
    
    "answer_options": [
        {"text": "{{ option_a_text }}", "isCorrect": {{ option_a_correct }}},
        {"text": "{{ option_b_text }}", "isCorrect": {{ option_b_correct }}},
        {"text": "{{ option_c_text }}", "isCorrect": {{ option_c_correct }}}
    ],
    
    "explanation": "{{ explanation_text }}{% if option_a_correct %}\n\nThe correct answer is {{ option_a_text }} because {{ option_a_rationale }}{% elif option_b_correct %}\n\nThe correct answer is {{ option_b_text }} because {{ option_b_rationale }}{% elif option_c_correct %}\n\nThe correct answer is {{ option_c_text }} because {{ option_c_rationale }}{% endif %}\n\n{% if incorrect_rationale %}The other options are incorrect because {{ incorrect_rationale }}{% endif %}",
    
    "references": [
        {"title": "{{ reference_title }}", "section": "{{ reference_section }}"}
    ]
}
""",
            template_id="management_decision",
            template_type="management",
            metadata={
                "description": "Template for management decision questions",
                "required_variables": [
                    "patient_age", "patient_gender", "diagnosis", 
                    "clinical_context", "lead_in_phrase", 
                    "option_a_text", "option_a_correct", 
                    "option_b_text", "option_b_correct", 
                    "option_c_text", "option_c_correct", 
                    "explanation_text", "reference_title", "reference_section"
                ],
                "optional_variables": [
                    "emergency_situation", "option_a_rationale", "option_b_rationale", 
                    "option_c_rationale", "incorrect_rationale"
                ]
            }
        )
        
        # Complication management template
        complication_template = QuestionTemplate(
            template_text="""
{# Complication Management Template #}
{# This template creates a complication management question following SESATS guidelines #}
{
    "stem": "A {{ patient_age }}-year-old {{ patient_gender }} undergoes {{ procedure_name }}. {{ procedure_details }}. {% if time_after_surgery %}{{ time_after_surgery }} after surgery, {% endif %}the patient develops {{ complication_description }}. {{ additional_findings }}.\n\n{{ lead_in_phrase }}",
    
    "answer_options": [
        {"text": "{{ option_a_text }}", "isCorrect": {{ option_a_correct }}},
        {"text": "{{ option_b_text }}", "isCorrect": {{ option_b_correct }}},
        {"text": "{{ option_c_text }}", "isCorrect": {{ option_c_correct }}}
    ],
    
    "explanation": "{{ explanation_text }}",
    
    "references": [
        {"title": "{{ reference_title }}", "section": "{{ reference_section }}"}
    ]
}
""",
            template_id="complication_management",
            template_type="complication",
            metadata={
                "description": "Template for complication management questions",
                "required_variables": [
                    "patient_age", "patient_gender", "procedure_name", 
                    "procedure_details", "complication_description", "lead_in_phrase", 
                    "option_a_text", "option_a_correct", 
                    "option_b_text", "option_b_correct", 
                    "option_c_text", "option_c_correct", 
                    "explanation_text", "reference_title", "reference_section"
                ],
                "optional_variables": [
                    "time_after_surgery", "additional_findings"
                ]
            }
        )
        
        # Register and save the templates
        templates = [clinical_template, management_template, complication_template]
        for template in templates:
            self.register_template(template)
            template_path = os.path.join(self.template_dir, f"{template.template_id}.json")
            template.save_to_file(template_path)
    
    def get_template(self, template_id: str) -> Optional[QuestionTemplate]:
        """
        Get question template by ID
        
        Args:
            template_id: Template identifier
            
        Returns:
            QuestionTemplate instance or None if not found
        """
        # Override to return QuestionTemplate instead of Template
        template = super().get_template(template_id)
        if template and not isinstance(template, QuestionTemplate):
            # Convert base Template to QuestionTemplate
            return QuestionTemplate(
                template_text=template.template_text,
                template_id=template.template_id
            )
        return template
    
    def get_templates_by_type(self, template_type: str) -> List[QuestionTemplate]:
        """
        Get templates of a specific type
        
        Args:
            template_type: Type of templates to retrieve
            
        Returns:
            List of matching templates
        """
        result = []
        for template_id in self.list_templates():
            template = self.get_template(template_id)
            if template and template.template_type == template_type:
                result.append(template)
        return result
    
    def create_template(self, 
                       template_text: str, 
                       template_id: str,
                       template_type: str = "clinical_scenario",
                       metadata: Optional[Dict[str, Any]] = None,
                       save_to_disk: bool = True) -> QuestionTemplate:
        """
        Create a new question template
        
        Args:
            template_text: Template text
            template_id: Template identifier
            template_type: Template type
            metadata: Optional metadata
            save_to_disk: Whether to save the template to disk
            
        Returns:
            Created template
        """
        template = QuestionTemplate(
            template_text=template_text,
            template_id=template_id,
            template_type=template_type,
            metadata=metadata
        )
        
        # Register with renderer
        self.register_template(template)
        
        # Save to disk if requested
        if save_to_disk:
            template_path = os.path.join(self.template_dir, f"{template_id}.json")
            template.save_to_file(template_path)
        
        return template 