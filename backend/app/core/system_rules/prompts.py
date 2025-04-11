from typing import Dict, Any, List, Optional, Union
import logging
import string
import re

from backend.app.core.system_rules.rules import SystemRules, SESATSRules

# Setup logger
logger = logging.getLogger("app.core.system_rules.prompts")

class PromptTemplate:
    """
    Base class for prompt templates
    
    Handles template rendering with variable substitution.
    """
    
    def __init__(self, template: str, rules: Optional[SystemRules] = None):
        """
        Initialize prompt template
        
        Args:
            template: Template string with {variable} placeholders
            rules: Optional system rules for variable values
        """
        self.template = template
        self.rules = rules
        
    def render(self, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Render the template with variables
        
        Args:
            variables: Dictionary of variable values
            
        Returns:
            Rendered template
        """
        variables = variables or {}
        
        try:
            # Use string.Template for variable substitution
            template = string.Template(self.template)
            return template.substitute(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            # Return template with unsubstituted variables
            return self.template
        
    def get_variables(self) -> List[str]:
        """
        Get list of variables in the template
        
        Returns:
            List of variable names
        """
        # Find all {variable} patterns in the template
        pattern = r'\{([a-zA-Z0-9_]+)\}'
        return re.findall(pattern, self.template)


class SESATSPromptTemplate(PromptTemplate):
    """
    Prompt template with SESATS guidelines
    
    Extends prompt template with SESATS rules.
    """
    
    def __init__(self, template: str, rules: Optional[SESATSRules] = None):
        """
        Initialize SESATS prompt template
        
        Args:
            template: Template string with {variable} placeholders
            rules: Optional SESATS rules
        """
        super().__init__(template, rules or SESATSRules())
        
    def render_with_guidelines(self, 
                               include_stem: bool = True,
                               include_responses: bool = True,
                               include_examples: bool = True,
                               additional_variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Render template with SESATS guidelines
        
        Args:
            include_stem: Include stem guidelines
            include_responses: Include response guidelines
            include_examples: Include example questions
            additional_variables: Additional variables for the template
            
        Returns:
            Rendered template with guidelines
        """
        rules = self.rules
        sesats_rules = SESATSRules() if not isinstance(rules, SESATSRules) else rules
        
        variables = additional_variables or {}
        
        if include_stem:
            stem_guidelines = sesats_rules.get_stem_guidelines()
            variables['stem_format'] = self._format_list(stem_guidelines.get('format', []))
            variables['stem_should_include'] = self._format_list(stem_guidelines.get('should_include', []))
            variables['stem_best_practice'] = stem_guidelines.get('best_practice', '')
            variables['lead_in_examples'] = self._format_list(sesats_rules.get_lead_in_examples())
            variables['things_to_avoid'] = self._format_list(sesats_rules.get_things_to_avoid())
            
        if include_responses:
            response_guidelines = sesats_rules.get_response_guidelines()
            variables['response_structure'] = self._format_list(response_guidelines.structure)
            variables['response_rules'] = self._format_list(response_guidelines.rules)
            variables['formatting_guidelines'] = self._format_list(response_guidelines.formatting_guidelines)
            variables['trick_avoidance'] = self._format_list(response_guidelines.trick_avoidance)
            
        if include_examples:
            example = sesats_rules.get_example()
            variables['example_stem'] = example.stem
            variables['example_options'] = self._format_list(example.answer_options)
            variables['example_critique'] = example.critique
            
        return self.render(variables)
    
    def _format_list(self, items: List[str]) -> str:
        """
        Format a list of items as a bulleted string
        
        Args:
            items: List of items
            
        Returns:
            Bulleted string
        """
        if not items:
            return ""
            
        return "\n".join([f"• {item}" for item in items])
    
    
# Common SESATS prompt templates
QUESTION_GENERATOR_TEMPLATE = """
You are a medical education specialist creating high-quality questions for the SESATS (Self-Education Self-Assessment in Thoracic Surgery) program.

# SESATS Guidelines
## Stem Format
{stem_format}

## Stem Should Include
{stem_should_include}

## Best Practice
{stem_best_practice}

## Lead-in Examples
{lead_in_examples}

## Things to Avoid
{things_to_avoid}

## Response Structure
{response_structure}

## Response Rules
{response_rules}

## Formatting Guidelines
{formatting_guidelines}

## Trick Avoidance
{trick_avoidance}

# Example Question
Stem:
{example_stem}

Options:
{example_options}

Critique:
{example_critique}

# Your Task
{task_description}

{additional_instructions}
"""

QUESTION_EVALUATOR_TEMPLATE = """
You are a medical education assessor evaluating questions for the SESATS (Self-Education Self-Assessment in Thoracic Surgery) program.

# SESATS Guidelines
## Stem Format
{stem_format}

## Stem Should Include
{stem_should_include}

## Best Practice
{stem_best_practice}

## Things to Avoid
{things_to_avoid}

## Response Rules
{response_rules}

## Formatting Guidelines
{formatting_guidelines}

# Evaluation Criteria
{evaluation_criteria}

# Your Task
{task_description}

{additional_instructions}
"""

def get_question_generator_prompt(task_description: str, 
                                 additional_instructions: str = "",
                                 rules: Optional[SESATSRules] = None) -> str:
    """
    Get a question generator prompt with SESATS guidelines
    
    Args:
        task_description: Description of the question generation task
        additional_instructions: Additional instructions for the question generator
        rules: Optional SESATS rules
        
    Returns:
        Rendered prompt
    """
    template = SESATSPromptTemplate(QUESTION_GENERATOR_TEMPLATE, rules)
    return template.render_with_guidelines(
        additional_variables={
            'task_description': task_description,
            'additional_instructions': additional_instructions
        }
    )

def get_question_evaluator_prompt(task_description: str,
                                 evaluation_criteria: str,
                                 additional_instructions: str = "",
                                 rules: Optional[SESATSRules] = None) -> str:
    """
    Get a question evaluator prompt with SESATS guidelines
    
    Args:
        task_description: Description of the question evaluation task
        evaluation_criteria: Specific criteria for evaluation
        additional_instructions: Additional instructions for the evaluator
        rules: Optional SESATS rules
        
    Returns:
        Rendered prompt
    """
    template = SESATSPromptTemplate(QUESTION_EVALUATOR_TEMPLATE, rules)
    return template.render_with_guidelines(
        include_examples=False,
        additional_variables={
            'task_description': task_description,
            'evaluation_criteria': evaluation_criteria,
            'additional_instructions': additional_instructions
        }
    ) 