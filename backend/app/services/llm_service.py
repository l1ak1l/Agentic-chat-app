"""
LLM service using Groq API with LangChain integration.
Provides streaming and non-streaming text generation capabilities.
"""

from typing import AsyncGenerator, Optional
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.callbacks import AsyncCallbackHandler, BaseCallbackHandler
from langchain_core.outputs import LLMResult
import asyncio
import logging
from ..core.config import get_settings
from ..core.utils import log_error, validate_api_keys, clean_unicode_text, sanitize_secret, mask_secret


class StreamingCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""
    
    def __init__(self):
        self.tokens = []
        self.token_queue = asyncio.Queue()
        self.finished = False
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Handle new token generation."""
        await self.token_queue.put(token)
    
    async def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Handle LLM completion."""
        self.finished = True
        await self.token_queue.put(None)  # Signal completion
    
    async def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Handle LLM errors."""
        self.finished = True
        await self.token_queue.put(None)  # Signal completion even on error


class LLMService:
    """Service for interacting with Groq LLM through LangChain."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self._validate_configuration()
        self._initialize_llm()
    
    def _validate_configuration(self) -> None:
        """Validate that required configuration is present."""
        try:
            validate_api_keys(
                groq_api_key=self.settings.groq_api_key
            )
            # Sanitize and store the API key
            self._groq_api_key = sanitize_secret(self.settings.groq_api_key)
            self.logger.info(f"Groq API key validated: {mask_secret(self._groq_api_key)}")
        except ValueError as e:
            self.logger.error(f"LLM Service configuration error: {e}")
            raise
    
    def _initialize_llm(self) -> None:
        """Initialize the Groq LLM instance."""
        try:
            self.llm = ChatGroq(
                groq_api_key=self._groq_api_key,
                model=self.settings.groq_model,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens
            )
            self.logger.info(f"LLM service initialized with model: {self.settings.groq_model}")
        except Exception as e:
            log_error(e, "LLM initialization")
            raise
    
    async def generate_response(self, query: str, context: Optional[str] = None) -> str:
        """Generate a non-streaming response to a query."""
        try:
            messages = self._prepare_messages(query, context)
            response = await self.llm.ainvoke(messages)
            return str(response.content)
        except Exception as e:
            log_error(e, "LLM response generation")
            return f"Error generating response: {str(e)}"
    
    async def stream_response(self, query: str, context: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Generate a streaming response to a query."""
        try:
            messages = self._prepare_messages(query, context)
            
            # Use astream for proper token streaming
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            log_error(e, "LLM streaming response")
            yield f"Error generating streaming response: {str(e)}"
    
    def _prepare_messages(self, query: str, context: Optional[str] = None):
        """Prepare messages for LLM input."""
        messages = []
        
        # Clean the query text to avoid Unicode encoding issues
        clean_query = clean_unicode_text(query)
        
        if context:
            clean_context = clean_unicode_text(context)
            system_prompt = f"""You are a helpful AI assistant that answers questions based on the provided context.
            
Context information:
{clean_context}

Please provide accurate and helpful answers based on this context. If the context doesn't contain enough information to answer the question, acknowledge this and provide the best answer you can based on your general knowledge."""
            messages.append(SystemMessage(content=clean_unicode_text(system_prompt)))
        else:
            system_prompt = "You are a helpful AI assistant. Provide accurate and helpful responses to user questions."
            messages.append(SystemMessage(content=system_prompt))
        
        messages.append(HumanMessage(content=clean_query))
        return messages


# Global LLM service instance
_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get or create the LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service