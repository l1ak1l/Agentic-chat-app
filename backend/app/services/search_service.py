"""
Search service using Tavily API with LangChain integration.
Provides web search capabilities for external knowledge retrieval.
"""

from typing import List, Dict, Any, Optional
from langchain_tavily import TavilySearch
import logging
from ..core.config import get_settings
from ..core.utils import log_error, validate_api_keys, sanitize_secret, mask_secret


class SearchService:
    """Service for web search using Tavily API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self._validate_configuration()
        self._initialize_search_tool()
    
    def _validate_configuration(self) -> None:
        """Validate that required configuration is present."""
        try:
            validate_api_keys(
                tavily_api_key=self.settings.tavily_api_key
            )
            # Sanitize and store the API key
            self._tavily_api_key = sanitize_secret(self.settings.tavily_api_key)
            self.logger.info(f"Tavily API key validated: {mask_secret(self._tavily_api_key)}")
        except ValueError as e:
            self.logger.error(f"Search Service configuration error: {e}")
            raise
    
    def _initialize_search_tool(self) -> None:
        """Initialize the Tavily search tool."""
        try:
            self.search_tool = TavilySearch(
                api_key=self._tavily_api_key,
                max_results=self.settings.tavily_max_results
            )
            self.logger.info("Search service initialized with Tavily")
        except Exception as e:
            log_error(e, "Search tool initialization")
            raise
    
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Perform a web search and return results."""
        try:
            self.logger.info(f"Performing search for query: {query}")
            
            # Use the Tavily search tool
            results = await self.search_tool.ainvoke(query)
            
            # Ensure results is a list
            if not isinstance(results, list):
                results = [results] if results else []
            
            self.logger.info(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            log_error(e, f"Search operation for query: {query}")
            return []
    
    async def search_and_format(self, query: str) -> str:
        """Perform search and return formatted results for LLM context."""
        results = await self.search(query)
        return self._format_search_results(results)
    
    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM context."""
        if not results:
            return "No search results found."
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            # Handle different result formats from Tavily
            if isinstance(result, dict):
                title = result.get("title", result.get("name", "Unknown Title"))
                content = result.get("content", result.get("snippet", result.get("description", "")))
                url = result.get("url", result.get("link", ""))
            else:
                # Handle string results
                title = f"Result {i}"
                content = str(result)
                url = ""
            
            formatted_result = f"{i}. {title}"
            if content:
                # Limit content length to avoid token limits
                content_preview = content[:500] + "..." if len(content) > 500 else content
                formatted_result += f"\n{content_preview}"
            if url:
                formatted_result += f"\nSource: {url}"
                
            formatted_results.append(formatted_result)
        
        return "\n\n".join(formatted_results)
    
    def is_search_needed(self, query: str) -> bool:
        """Determine if a search is needed based on the query."""
        # Keywords that suggest current/real-time information is needed
        search_indicators = [
            "latest", "recent", "current", "today", "now", "2024", "2025",
            "news", "update", "what happened", "breaking", "price",
            "weather", "stock", "market"
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in search_indicators)


# Global search service instance
_search_service: Optional[SearchService] = None

def get_search_service() -> SearchService:
    """Get or create the search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service