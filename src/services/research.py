"""Research service using Tavily API for production-grade web search."""
import httpx
import logging
from typing import Optional
import anyio
from src.config import settings

logger = logging.getLogger(__name__)

class ResearchError(Exception):
    """Raised when research operations fail."""
    pass

async def search_tavily(query: str, limit: Optional[int] = None) -> str:
    """
    Search the web using Tavily API (production-grade).
    
    Args:
        query: Search query
        limit: Maximum number of results (uses DEFAULT_SEARCH_LIMIT if None)
        
    Returns:
        Formatted search results or error message
        
    Note:
        Tavily provides AI-optimized search results with clean content extraction.
    """
    if limit is None:
        limit = settings.DEFAULT_SEARCH_LIMIT
    
    # Validate limit
    limit = max(1, min(limit, 10))  # Clamp between 1-10
    
    try:
        from tavily import TavilyClient
        
        def _search():
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            return client.search(
                query=query,
                max_results=limit,
                search_depth="basic",  # "basic" or "advanced"
                include_answer=True,
                include_raw_content=False
            )
        
        # Run in thread to avoid blocking
        response = await anyio.to_thread.run_sync(_search)
        
        if not response or 'results' not in response:
            logger.warning(f"No results from Tavily for query: {query}")
            return "No results found."
        
        # Format results
        formatted_results = []
        
        # Include AI-generated answer if available
        if response.get('answer'):
            formatted_results.append(f"**Answer**: {response['answer']}\n")
        
        # Add search results
        for idx, result in enumerate(response['results'], 1):
            formatted_results.append(
                f"**Result {idx}**\n"
                f"Title: {result.get('title', 'N/A')}\n"
                f"URL: {result.get('url', 'N/A')}\n"
                f"Content: {result.get('content', 'N/A')}\n"
            )
        
        logger.info(f"Tavily search successful: {query} ({len(response['results'])} results)")
        return "\n---\n".join(formatted_results)
        
    except ImportError:
        logger.error("Tavily client not installed")
        return "Error: Tavily client not installed. Run: pip install tavily-python"
    except Exception as e:
        logger.error(f"Tavily search error for '{query}': {e}")
        return f"Error performing search: {str(e)}"

async def fetch_page_content(url: str) -> str:
    """
    Fetch and extract text content from a URL.
    
    Args:
        url: URL to fetch
        
    Returns:
        Extracted text content or error message
        
    Note:
        Uses httpx with proper headers and timeout.
        Falls back to basic extraction if advanced parsing fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.HTTP_TIMEOUT,
            headers=headers
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
        
        # Try BeautifulSoup for better extraction
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'iframe']):
                element.decompose()
            
            # Try to find main content area first
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.body
            
            if main_content:
                # Extract text from main content
                text = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to full body
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = []
            for line in text.splitlines():
                line = line.strip()
                if line and len(line) > 2:  # Skip very short lines
                    lines.append(line)
            
            clean_text = '\n'.join(lines)
            
            # Remove excessive newlines
            import re
            clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)
            
        except ImportError:
            logger.warning("BeautifulSoup not available, using basic extraction")
            clean_text = response.text[:5000]  # Just take first 5000 chars
        
        # Limit response size
        MAX_CONTENT_LENGTH = 10000
        if len(clean_text) > MAX_CONTENT_LENGTH:
            clean_text = clean_text[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"
        
        logger.info(f"Successfully fetched content from: {url} ({len(clean_text)} chars)")
        return clean_text
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching {url}: {e.response.status_code}")
        return f"Error: HTTP {e.response.status_code} - {e.response.reason_phrase}"
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching {url}")
        return f"Error: Request timed out after {settings.HTTP_TIMEOUT} seconds"
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return f"Error fetching content: {str(e)}"
