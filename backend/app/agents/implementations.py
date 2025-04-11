import logging

from backend.app.agents.factory import AgentFactory
from backend.app.agents.implementations import (
    QuestionGeneratorAgent,
    SystemRulesAgent,
    DocumentLoaderAgent,
    QuestionEvaluatorAgent,
    MultipleChoiceFormatterAgent,
    ContrarianReviewerAgent,
    QuestionImproverAgent,
    QuestionVerifierAgent,
    SurgicalSituationValidatorAgent,
    FinalFormatterAgent
)

# Setup logger
logger = logging.getLogger("app.agents.implementations")

# Register agent implementations with the factory
AgentFactory.register("document_loader", DocumentLoaderAgent)
AgentFactory.register("question_generator", QuestionGeneratorAgent)
AgentFactory.register("question_evaluator", QuestionEvaluatorAgent)
AgentFactory.register("system_rules", SystemRulesAgent)
AgentFactory.register("multiple_choice_formatter", MultipleChoiceFormatterAgent)
AgentFactory.register("contrarian_reviewer", ContrarianReviewerAgent)
AgentFactory.register("question_improver", QuestionImproverAgent)
AgentFactory.register("question_verifier", QuestionVerifierAgent)
AgentFactory.register("surgical_situation_validator", SurgicalSituationValidatorAgent)
AgentFactory.register("final_formatter", FinalFormatterAgent) 