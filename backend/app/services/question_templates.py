"""
Question template service for generating and managing question templates
"""
from typing import Dict, Any, List, Optional, Union
import logging
import os
from pathlib import Path

from backend.app.core.templates import QuestionTemplate, QuestionTemplateLoader
from backend.app.core.system_rules.rules import SESATSRules

# Setup logger
logger = logging.getLogger("app.services.question_templates")

class QuestionTemplateService:
    """
    Service for question template operations
    
    This service provides high-level operations for working with question templates,
    including generation, validation, and management.
    """
    
    def __init__(self):
        """Initialize the question template service"""
        self.loader = QuestionTemplateLoader()
        self.sesats_rules = SESATSRules()
    
    def get_template(self, template_id: str) -> Optional[QuestionTemplate]:
        """
        Get a template by ID
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template or None if not found
        """
        return self.loader.get_template(template_id)
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """
        Get all available templates
        
        Returns:
            List of template metadata dictionaries
        """
        result = []
        template_ids = self.loader.list_templates()
        
        for template_id in template_ids:
            template = self.loader.get_template(template_id)
            if template:
                # Include basic info and metadata
                template_info = {
                    "id": template.template_id,
                    "type": template.template_type,
                    "variables": template.get_variables(),
                    "has_conditionals": len(template.get_conditionals()) > 0
                }
                
                # Add metadata if available
                if hasattr(template, "metadata") and template.metadata:
                    template_info.update({
                        "description": template.metadata.get("description", ""),
                        "required_variables": template.metadata.get("required_variables", []),
                        "optional_variables": template.metadata.get("optional_variables", [])
                    })
                
                result.append(template_info)
        
        return result
    
    def get_templates_by_type(self, template_type: str) -> List[Dict[str, Any]]:
        """
        Get templates by type
        
        Args:
            template_type: Type of templates to get
            
        Returns:
            List of template metadata dictionaries
        """
        templates = self.loader.get_templates_by_type(template_type)
        return [
            {
                "id": t.template_id,
                "type": t.template_type,
                "variables": t.get_variables(),
                "description": t.metadata.get("description", "") if hasattr(t, "metadata") else "",
                "required_variables": t.metadata.get("required_variables", []) if hasattr(t, "metadata") else [],
                "optional_variables": t.metadata.get("optional_variables", []) if hasattr(t, "metadata") else []
            }
            for t in templates
        ]
    
    def render_template(self, 
                       template_id: str, 
                       variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a template with variables
        
        Args:
            template_id: Template identifier
            variables: Dictionary of variable values
            
        Returns:
            Dictionary with rendered question components
        """
        template = self.loader.get_template(template_id)
        
        if not template:
            logger.error(f"Template not found: {template_id}")
            return {"error": f"Template not found: {template_id}"}
        
        try:
            # Add SESATS guidelines to variables if applicable
            result = template.render_with_guidelines(variables)
            
            # Add metadata about the template used
            result["_metadata"] = {
                "template_id": template_id,
                "template_type": template.template_type if hasattr(template, "template_type") else "unknown"
            }
            
            return result
        except Exception as e:
            logger.error(f"Error rendering template {template_id}: {e}")
            return {"error": f"Error rendering template: {str(e)}"}
    
    def validate_template_variables(self, 
                                  template_id: str, 
                                  variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate variables for a template
        
        Args:
            template_id: Template identifier
            variables: Variables to validate
            
        Returns:
            Validation results dictionary
        """
        template = self.loader.get_template(template_id)
        
        if not template:
            return {
                "valid": False,
                "missing_required": [],
                "error": f"Template not found: {template_id}"
            }
        
        # Get required variables from metadata or by parsing the template
        required_vars = []
        if hasattr(template, "metadata") and "required_variables" in template.metadata:
            required_vars = template.metadata["required_variables"]
        else:
            # Simple heuristic: variables without defaults in the template are required
            # This is a simplification - a more robust solution would parse the template
            required_vars = template.get_variables()
        
        # Check for missing required variables
        missing = [var for var in required_vars if var not in variables]
        
        return {
            "valid": len(missing) == 0,
            "missing_required": missing,
            "template_id": template_id
        }
    
    def create_template(self, 
                      template_text: str, 
                      template_id: str,
                      template_type: str = "clinical_scenario",
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new template
        
        Args:
            template_text: Raw template text
            template_id: Template identifier
            template_type: Template type
            metadata: Optional metadata
            
        Returns:
            Template info dictionary
        """
        try:
            template = self.loader.create_template(
                template_text=template_text,
                template_id=template_id,
                template_type=template_type,
                metadata=metadata,
                save_to_disk=True
            )
            
            return {
                "id": template.template_id,
                "type": template.template_type,
                "variables": template.get_variables(),
                "has_conditionals": len(template.get_conditionals()) > 0,
                "created": True
            }
        except Exception as e:
            logger.error(f"Error creating template {template_id}: {e}")
            return {
                "id": template_id,
                "created": False,
                "error": str(e)
            }
    
    def get_available_template_types(self) -> List[Dict[str, str]]:
        """
        Get all available template types
        
        Returns:
            List of template type dictionaries
        """
        return [
            {"id": type_id, "description": description}
            for type_id, description in QuestionTemplate.TEMPLATE_TYPES.items()
        ] 