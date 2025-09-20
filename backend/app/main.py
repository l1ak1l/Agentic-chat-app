"""
FastAPI application entry point.
Main application setup with CORS, middleware, and routing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .core.config import get_settings
from .core.utils import setup_logging
from .api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Load environment variables
    from .core.utils import load_environment
    load_environment()
    
    # Startup
    settings = get_settings()
    setup_logging("INFO" if not settings.debug else "DEBUG")
    
    logger = logging.getLogger(__name__)
    logger.info("Starting FastAPI RAG backend...")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Verify services can be initialized
    try:
        from .services.llm_service import get_llm_service
        from .services.search_service import get_search_service
        from .chains.rag_chain import get_rag_chain
        
        # Initialize services
        llm_service = get_llm_service()
        search_service = get_search_service()
        rag_chain = get_rag_chain()
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        logger.warning("Application starting but some services may not work properly")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI RAG backend...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="RAG Backend API",
        description="Production-ready FastAPI backend with LangChain-Groq LLM and Tavily search",
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=settings.cors_methods,
        allow_headers=settings.cors_headers,
    )
    
    # Include routers
    app.include_router(router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "FastAPI RAG Backend",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "chat_streaming": "/api/v1/chat",
                "chat_simple": "/api/v1/chat/simple",
                "health": "/api/v1/health",
                "docs": "/docs",
                "openapi": "/openapi.json"
            }
        }
    
    return app


# Create app instance
app = create_app()