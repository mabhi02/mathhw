"""
Base template system for ABTS
"""
from typing import Dict, Any, List, Optional, Callable, Union
import re
import logging
import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template as JinjaTemplate

from backend.app.config import get_settings

# Setup logger
logger = logging.getLogger("app.core.templates")

class Template:
    """
    Base class for templates
    
    This class provides the foundation for all templates in the system,
    with support for variable substitution and conditional logic.
    """
    
    def __init__(self, template_text: str, template_id: Optional[str] = None):
        """
        Initialize template
        
        Args:
            template_text: Raw template text with Jinja2 syntax
            template_id: Optional identifier for this template
        """
        self.template_text = template_text
        self.template_id = template_id or "unknown"
        self._jinja_template = None
        self._init_template()
        
    def _init_template(self):
        """Initialize the Jinja2 template"""
        try:
            env = Environment(autoescape=select_autoescape(['html', 'xml']))
            self._jinja_template = env.from_string(self.template_text)
        except Exception as e:
            logger.error(f"Error initializing template {self.template_id}: {e}")
            # Create a simple pass-through template
            self._jinja_template = JinjaTemplate("{{ _error }}")
    
    def render(self, variables: Dict[str, Any] = None) -> str:
        """
        Render the template with variables
        
        Args:
            variables: Dictionary of variables to substitute
            
        Returns:
            Rendered template
        """
        variables = variables or {}
        
        try:
            # Include the template_id in the variables
            variables["_template_id"] = self.template_id
            
            # If there was an initialization error, return it
            if self._jinja_template is None or "_error" in self._jinja_template.render():
                variables["_error"] = f"Template error: Failed to initialize template {self.template_id}"
                return "Template error: Failed to initialize template"
                
            return self._jinja_template.render(**variables)
        except Exception as e:
            logger.error(f"Error rendering template {self.template_id}: {e}")
            return f"Template error: {str(e)}"
    
    def get_variables(self) -> List[str]:
        """
        Get a list of all variables in the template
        
        Returns:
            List of variable names
        """
        if not self.template_text:
            return []
            
        # This is a simple regex to find {{ variable }} patterns
        # A more robust solution would use the Jinja parser
        pattern = r'{{\s*([a-zA-Z0-9_]+)\s*}}'
        return re.findall(pattern, self.template_text)
    
    def get_conditionals(self) -> List[str]:
        """
        Get a list of all conditional blocks in the template
        
        Returns:
            List of conditional expressions
        """
        if not self.template_text:
            return []
            
        # Simple regex to find {% if condition %} patterns
        pattern = r'{%\s*if\s+(.+?)\s*%}'
        return re.findall(pattern, self.template_text)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary representation
        
        Returns:
            Dictionary with template data
        """
        return {
            "template_id": self.template_id,
            "template_text": self.template_text,
            "variables": self.get_variables(),
            "conditionals": self.get_conditionals()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """
        Create template from dictionary
        
        Args:
            data: Dictionary with template data
            
        Returns:
            Template instance
        """
        return cls(
            template_text=data.get("template_text", ""),
            template_id=data.get("template_id")
        )
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Template':
        """
        Load template from file
        
        Args:
            file_path: Path to template file
            
        Returns:
            Template instance
        """
        try:
            file_path = Path(file_path)
            template_id = file_path.stem
            
            with open(file_path, 'r') as f:
                template_text = f.read()
                
            return cls(template_text=template_text, template_id=template_id)
        except Exception as e:
            logger.error(f"Error loading template from {file_path}: {e}")
            return cls(template_text="", template_id="error")
    
    def save_to_file(self, file_path: Union[str, Path]) -> bool:
        """
        Save template to file
        
        Args:
            file_path: Path to save template
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'w') as f:
                f.write(self.template_text)
            return True
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {e}")
            return False


class TemplateRenderer:
    """
    Base class for template rendering
    
    This class provides functionality to load and render templates
    from a template directory.
    """
    
    def __init__(self, template_dir: Optional[Union[str, Path]] = None):
        """
        Initialize template renderer
        
        Args:
            template_dir: Directory containing templates, defaults to settings
        """
        settings = get_settings()
        self.template_dir = template_dir or settings.TEMPLATE_PATH
        self.env = self._create_environment()
        self._templates = {}
        
    def _create_environment(self) -> Environment:
        """
        Create Jinja2 environment
        
        Returns:
            Configured Jinja2 environment
        """
        try:
            loader = FileSystemLoader(self.template_dir)
            env = Environment(
                loader=loader,
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            return env
        except Exception as e:
            logger.error(f"Error creating Jinja2 environment: {e}")
            # Create minimal environment without loader
            return Environment()
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """
        Get template by ID
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template instance or None if not found
        """
        # Check if already loaded
        if template_id in self._templates:
            return self._templates[template_id]
            
        # Try to load from template directory
        try:
            template_path = os.path.join(self.template_dir, f"{template_id}.j2")
            if os.path.exists(template_path):
                template = Template.from_file(template_path)
                self._templates[template_id] = template
                return template
        except Exception as e:
            logger.error(f"Error loading template {template_id}: {e}")
            
        return None
    
    def render_template(self, template_id: str, variables: Dict[str, Any] = None) -> str:
        """
        Render template with variables
        
        Args:
            template_id: Template identifier
            variables: Variables for rendering
            
        Returns:
            Rendered template text or error message
        """
        template = self.get_template(template_id)
        if template:
            return template.render(variables)
        else:
            return f"Template not found: {template_id}"
    
    def register_template(self, template: Template) -> None:
        """
        Register a template with the renderer
        
        Args:
            template: Template instance
        """
        self._templates[template.template_id] = template
        logger.info(f"Registered template: {template.template_id}")
    
    def list_templates(self) -> List[str]:
        """
        List all available template IDs
        
        Returns:
            List of template IDs
        """
        template_files = []
        try:
            # Get templates from disk
            for f in os.listdir(self.template_dir):
                if f.endswith('.j2'):
                    template_files.append(os.path.splitext(f)[0])
            
            # Add templates from memory
            template_files.extend(self._templates.keys())
            
            # Remove duplicates and sort
            return sorted(list(set(template_files)))
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return list(self._templates.keys()) 