"""
Utility functions for the FastAPI backend.
"""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime


def setup_logging(level: str = "INFO") -> None:
    """Setup application logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def format_search_results(results: list) -> str:
    """Format search results for LLM context."""
    if not results:
        return "No search results found."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "Unknown Title")
        content = result.get("content", "No content available")
        url = result.get("url", "")
        
        formatted_result = f"{i}. {title}\n{content[:500]}..."
        if url:
            formatted_result += f"\nSource: {url}"
        formatted_results.append(formatted_result)
    
    return "\n\n".join(formatted_results)


def create_sse_message(data: str, event: Optional[str] = None) -> str:
    """Create a Server-Sent Events formatted message."""
    message = f"data: {data}\n\n"
    if event:
        message = f"event: {event}\n{message}"
    return message


def log_error(error: Exception, context: str = "") -> None:
    """Log an error with context information."""
    logger = logging.getLogger(__name__)
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def clean_unicode_text(text: str) -> str:
    """Clean problematic Unicode characters that cause encoding issues."""
    if not text:
        return text
    
    # Replace line/paragraph separators with standard newlines
    text = text.replace('\u2028', '\n')  # Line separator
    text = text.replace('\u2029', '\n\n')  # Paragraph separator
    
    # Replace other problematic Unicode quotes/chars
    text = text.replace('\u2018', "'")  # Left single quote
    text = text.replace('\u2019', "'")  # Right single quote
    text = text.replace('\u201c', '"')  # Left double quote
    text = text.replace('\u201d', '"')  # Right double quote
    text = text.replace('\u202f', ' ')  # Narrow no-break space
    
    return text


def sanitize_secret(secret: str) -> str:
    """Sanitize API keys and secrets to ensure ASCII-only encoding."""
    if not secret:
        raise ValueError("Secret cannot be empty")
    
    # Strip whitespace
    secret = secret.strip()
    
    # Remove problematic control characters and separators
    secret = secret.replace('\r', '')  # Carriage return
    secret = secret.replace('\n', '')  # Line feed
    secret = secret.replace('\t', '')  # Tab
    secret = secret.replace('\u2028', '')  # Line separator
    secret = secret.replace('\u2029', '')  # Paragraph separator
    secret = secret.replace('\u200b', '')  # Zero-width space
    secret = secret.replace('\ufeff', '')  # BOM
    secret = secret.replace('\u00a0', '')  # Non-breaking space
    secret = secret.replace('\u202f', '')  # Narrow no-break space
    
    # Validate ASCII encoding
    try:
        secret.encode('ascii')
    except UnicodeEncodeError as e:
        raise ValueError(
            f"API key contains non-ASCII characters at position {e.start}: {repr(secret[e.start:e.end])}. "
            "Please check your API key for hidden Unicode characters and re-enter it."
        )
    
    if not secret:
        raise ValueError("Secret is empty after sanitization")
    
    return secret


def mask_secret(secret: str) -> str:
    """Create a masked version of a secret for logging."""
    if not secret or len(secret) < 8:
        return "***masked***"
    return f"{secret[:4]}...{secret[-4:]} (len:{len(secret)})"


def validate_api_keys(**kwargs) -> Dict[str, Any]:
    """Validate that required API keys are present."""
    missing_keys = []
    for key_name, key_value in kwargs.items():
        if not key_value:
            missing_keys.append(key_name)
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    return {"status": "valid", "timestamp": datetime.utcnow()}