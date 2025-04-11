# Question Templates

This directory contains templates for generating various types of medical education questions. These templates provide a structured format for creating consistent, high-quality questions that can be used for assessment and learning.

## Available Templates

1. **Multiple Choice Questions** (`multiple_choice.json`)
   - Standard multiple-choice questions with 3 options
   - One correct answer and two plausible distractors
   - Includes detailed explanation and references

2. **Short Answer Questions** (`short_answer.json`)
   - Questions requiring a brief, specific answer
   - Includes answer key, explanation, and relevant keywords

3. **Clinical Scenario Questions** (`clinical_scenario.json`)
   - Complex case-based scenarios requiring analysis and decision-making
   - Uses 3 answer options (1 correct, 2 plausible distractors)
   - Includes patient history, examination findings, and diagnostic results
   - Focuses on application of medical knowledge to realistic situations

4. **True/False Questions** (`true_false.json`)
   - Statement-based questions requiring true/false assessment
   - Includes detailed explanation of why the statement is true or false

## Template Structure

Each template follows a consistent structure:

- `template_id`: Unique identifier for the template
- `template_type`: Type of question (e.g., multiple_choice, short_answer)
- `version`: Version number for tracking changes
- `description`: Brief description of the template's purpose
- `format`: The structure of the question, including placeholders for content
- `instructions`: Guidelines for filling in each part of the template
- `examples`: Sample questions demonstrating proper use of the template

## Usage

1. Select the appropriate template based on your assessment needs
2. Replace the placeholders (in double curly braces, e.g., `{{question_text}}`) with your content
3. Follow the guidelines in the `instructions` section to ensure high-quality questions
4. Refer to the examples for guidance on how to structure your content

## Best Practices for Answer Options

Following SESATS guidelines:
- Multiple choice and clinical scenario questions should have exactly 3 options (1 correct, 2 distractors)
- All options should be similarly plausible to avoid obvious throwaway options
- Options should be of similar length and complexity
- Distractors should reflect common misconceptions
- Avoid absolute terms like "always," "never," or "all"

## Integration with Question Generation System

These templates are used by the question generation services to create properly formatted questions. The templates ensure that all generated questions follow a consistent structure and include all necessary components.

## Extending Templates

To create a new template:

1. Copy an existing template as a starting point
2. Modify the structure and placeholders as needed
3. Update the `template_id`, `template_type`, and `description`
4. Add appropriate instructions and examples
5. Add the new template to the `index.json` file

## Best Practices

- Focus on assessing application of knowledge rather than simple recall
- Use realistic scenarios that reflect actual clinical practice
- Include detailed explanations that teach as well as assess
- Target specific levels of Bloom's taxonomy appropriate to the learner level
- Ensure all options in multiple-choice questions are plausible but clearly distinguishable 