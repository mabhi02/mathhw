import logging
from typing import Dict, Optional
import json
from datetime import datetime
import os
from pathlib import Path

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.document_loader")

class DocumentLoaderAgent(AbstractAgent):
    """
    Agent for loading and processing documents
    
    This agent specializes in loading document content and extracting relevant
    information for downstream processing.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute document loading request
        
        Args:
            request: Agent request with document path or content
            
        Returns:
            Agent response with processed document
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Try to extract document path from prompt or parameters
            document_path = request.params.get("document_path")
            content = None
            
            # If document path is provided, load the document
            if document_path:
                if os.path.exists(document_path):
                    with open(document_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    return AgentResponse(
                        text=f"Error: Document not found at path {document_path}",
                        request_id=request.context.request_id,
                        agent_id=self.agent_id,
                        agent_name=self.name,
                        error=f"Document not found at path {document_path}",
                        success=False
                    )
            
            # If content wasn't loaded from a file, use the request prompt
            if not content:
                content = request.prompt
            
            # Process the document content with the LLM
            result = await self.llm_provider.generate(
                prompt=f"Please process and analyze the following document content:\n\n{content[:8000]}",  # limit size to avoid token limits
                system_prompt=system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Try to extract structured data
            output_data = {}
            try:
                # Check if response is JSON
                text = result.get("text", "")
                if text.startswith("{") and text.endswith("}"):
                    output_data = json.loads(text)
                else:
                    # Simple heuristic to extract key insights
                    lines = text.strip().split("\n")
                    key_points = [line for line in lines if line.strip()]
                    output_data = {
                        "content_summary": text,
                        "key_points": key_points[:10],  # First 10 key points
                        "content_type": "text",
                        "processed_length": len(content),
                    }
            except json.JSONDecodeError:
                # If response is not valid JSON, just provide basic metadata
                output_data = {
                    "content_summary": result.get("text", "")[:1000],
                    "processed_length": len(content),
                }
            
            return AgentResponse(
                text=result.get("text", ""),
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata={"model": result.get("model", "unknown"), "document_length": len(content)},
                success=result.get("success", False)
            )
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing document loader agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error processing document: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 