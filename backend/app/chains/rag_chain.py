"""
RAG (Retrieval-Augmented Generation) chain implementation.
Combines Tavily search with Groq LLM for enhanced responses.
"""

from typing import AsyncGenerator, Dict, Any, Optional
import logging
from ..services.llm_service import get_llm_service
from ..services.search_service import get_search_service
from ..core.utils import log_error


class RAGChain:
    """Retrieval-Augmented Generation chain combining search and LLM."""
    
    def __init__(self):
        self.llm_service = get_llm_service()
        self.search_service = None  # Initialize lazily
        self.logger = logging.getLogger(__name__)
    
    def _get_search_service(self):
        """Get search service lazily, handle missing API key gracefully."""
        if self.search_service is None:
            try:
                self.search_service = get_search_service()
            except Exception as e:
                self.logger.warning(f"Search service unavailable: {e}")
                self.search_service = False  # Mark as unavailable
        return self.search_service if self.search_service is not False else None
    
    async def run(self, query: str, use_search: bool = True) -> str:
        """Run the RAG chain and return a complete response."""
        try:
            context = None
            
            if use_search:
                search_service = self._get_search_service()
                # Check if search is needed and available
                if search_service and search_service.is_search_needed(query):
                    self.logger.info(f"Running search for query: {query}")
                    context = await search_service.search_and_format(query)
                else:
                    if not search_service:
                        self.logger.info("Search service unavailable, using LLM only")
                    else:
                        self.logger.info("Search not needed for this query")
            
            # Generate response using LLM with optional context
            response = await self.llm_service.generate_response(query, context)
            return response
            
        except Exception as e:
            log_error(e, "RAG chain execution")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
    
    async def stream(self, query: str, use_search: bool = True) -> AsyncGenerator[Dict[str, Any], None]:
        """Run the RAG chain with streaming response."""
        try:
            context = None
            search_results = []
            
            # Yield initial status using proper SSE format
            yield {"data": "Processing your request...", "event": "status"}
            
            if use_search:
                search_service = self._get_search_service()
                # Check if search is needed and available
                if search_service and search_service.is_search_needed(query):
                    yield {"data": "Searching for relevant information...", "event": "status"}
                    
                    # Get search results
                    search_results = await search_service.search(query)
                    context = search_service._format_search_results(search_results)
                    
                    # Yield search completion
                    yield {
                        "data": f"Found {len(search_results)} relevant sources",
                        "event": "search_complete"
                    }
                else:
                    if not search_service:
                        yield {"data": "Search unavailable, using existing knowledge...", "event": "status"}
                    else:
                        yield {"data": "Using existing knowledge...", "event": "status"}
            
            # Start streaming LLM response
            yield {"data": "Generating response...", "event": "status"}
            
            async for token in self.llm_service.stream_response(query, context):
                yield {"data": token, "event": "token"}
            
            # Yield completion status
            yield {"data": "Response complete", "event": "complete"}
            
        except Exception as e:
            log_error(e, "RAG chain streaming")
            yield {
                "data": f"Error processing request: {str(e)}",
                "event": "error"
            }
    
    async def run_with_metadata(self, query: str, use_search: bool = True) -> Dict[str, Any]:
        """Run the RAG chain and return response with metadata."""
        try:
            result = {
                "query": query,
                "response": "",
                "search_used": False,
                "search_results": [],
                "context_length": 0,
                "error": None
            }
            
            context = None
            
            if use_search:
                search_service = self._get_search_service()
                if search_service and search_service.is_search_needed(query):
                    self.logger.info(f"Running search for query: {query}")
                    search_results = await search_service.search(query)
                    context = search_service._format_search_results(search_results)
                    
                    result["search_used"] = True
                    result["search_results"] = search_results
                    result["context_length"] = len(context) if context else 0
            
            # Generate response
            response = await self.llm_service.generate_response(query, context)
            result["response"] = response
            
            return result
            
        except Exception as e:
            log_error(e, "RAG chain with metadata")
            return {
                "query": query,
                "response": f"Error processing request: {str(e)}",
                "search_used": False,
                "search_results": [],
                "context_length": 0,
                "error": str(e)
            }


# Global RAG chain instance
_rag_chain: Optional[RAGChain] = None

def get_rag_chain() -> RAGChain:
    """Get or create the RAG chain instance."""
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain