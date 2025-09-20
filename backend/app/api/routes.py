"""
API routes for the FastAPI backend.
Implements the /chat endpoint with Server-Sent Events streaming.
"""

import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import logging
from ..chains.rag_chain import get_rag_chain
from ..core.utils import create_sse_message, log_error


router = APIRouter()
logger = logging.getLogger(__name__)


async def stream_chat_response(query: str, use_search: bool = True):
    """Generate streaming response for chat endpoint."""
    try:
        rag_chain = get_rag_chain()
        
        async for chunk in rag_chain.stream(query, use_search):
            # EventSourceResponse will handle SSE formatting
            yield chunk
            
    except Exception as e:
        log_error(e, "Chat streaming response")
        yield {
            "type": "error",
            "message": f"Streaming error: {str(e)}"
        }


@router.get("/chat")
async def chat_stream(
    query: str = Query(..., description="The user's query/question"),
    use_search: bool = Query(True, description="Whether to use web search for context")
):
    """
    Stream chat responses using Server-Sent Events.
    
    Args:
        query: The user's question or message
        use_search: Whether to perform web search for additional context
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query parameter is required and cannot be empty")
        
        logger.info(f"Chat request received - Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        return EventSourceResponse(
            stream_chat_response(query.strip(), use_search),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Chat endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/chat")
async def chat_stream_post(
    request: dict
):
    """
    Stream chat responses using Server-Sent Events (POST version).
    
    Request body:
        {
            "query": "Your question here",
            "use_search": true
        }
    """
    try:
        query = request.get("query")
        use_search = request.get("use_search", True)
        
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query is required and cannot be empty")
        
        logger.info(f"Chat POST request received - Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        return EventSourceResponse(
            stream_chat_response(query.strip(), use_search),
            media_type="text/event-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "Chat POST endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/chat/simple")
async def chat_simple(
    query: str = Query(..., description="The user's query/question"),
    use_search: bool = Query(True, description="Whether to use web search for context")
):
    """
    Get a simple, non-streaming chat response.
    
    Args:
        query: The user's question or message
        use_search: Whether to perform web search for additional context
        
    Returns:
        JSON response with the answer and metadata
    """
    try:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query parameter is required and cannot be empty")
        
        logger.info(f"Simple chat request - Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        
        rag_chain = get_rag_chain()
        result = await rag_chain.run_with_metadata(query.strip(), use_search)
        
        return {
            "success": True,
            "data": result,
            "message": "Response generated successfully"
        }
        
    except Exception as e:
        log_error(e, "Simple chat endpoint")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "FastAPI RAG backend is running",
        "endpoints": {
            "streaming_chat": "/chat",
            "simple_chat": "/chat/simple",
            "health": "/health"
        }
    }