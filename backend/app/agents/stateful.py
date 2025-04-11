import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse, LLMAgent
from backend.app.agents.state import DatabaseStateMixin

# Setup logger
logger = logging.getLogger("app.agents.stateful")


class StatefulLLMAgent(DatabaseStateMixin, LLMAgent):
    """
    Stateful version of LLMAgent with database persistence
    
    This agent extends LLMAgent with database state persistence.
    """
    pass


class ConversationMemoryAgent(DatabaseStateMixin, LLMAgent):
    """
    LLM Agent with conversation memory
    
    This agent maintains a history of interactions in its state,
    allowing for conversational context across multiple requests.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute with conversation memory
        
        Args:
            request: Agent request
            
        Returns:
            Agent response
        """
        start_time = datetime.utcnow()
        
        # Initialize conversation history if not present
        if not hasattr(self, '_state') or not self._state:
            self._state = {
                "messages": []
            }
        
        # Add the new message to history
        self._state["messages"].append({
            "role": "user",
            "content": request.prompt,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Format conversation history for context
        history = "\n\n".join([
            f"[{msg['role']}]: {msg['content']}"
            for msg in self._state["messages"][-5:]  # Only use last 5 messages for context
        ])
        
        # Create a prompt with history
        prompt_with_history = f"Conversation history:\n{history}\n\nPlease respond to the latest message."
        
        # Execute with conversation context
        system_prompt = self.format_system_prompt(request)
        
        try:
            # Generate response using LLM
            result = await self.llm_provider.generate(
                prompt=prompt_with_history,
                system_prompt=system_prompt,
                **request.params
            )
            
            response_text = result.get("text", "")
            
            # Add assistant response to history
            self._state["messages"].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Create response
            response = AgentResponse(
                text=response_text,
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                metadata={
                    "model": result.get("model", "unknown"),
                    "conversation_turns": len(self._state["messages"]) // 2
                },
                success=True
            )
            
            return response
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing conversation agent: {str(e)}")
            
            return AgentResponse(
                text=f"Error: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 