from __future__ import annotations

from typing import Any

from langchain_core.tools import tool
from tavily import TavilyClient

from app.repositories.weaviate_repository import WeaviateRepository


def create_tavily_tool(api_key: str) -> Any:
    """
    Create a LangChain tool wrapper for Tavily search.

    Args:
        api_key: Tavily API key

    Returns:
        LangChain tool for Tavily search
    """
    tavily_client = TavilyClient(api_key=api_key)

    @tool
    def tavily_search(query: str) -> str:
        """
        Search the web for current information using Tavily.

        Use this tool when you need to find recent information, news, or
        information that might not be in the internal knowledge base.

        Args:
            query: Search query string

        Returns:
            Formatted string with search results
        """
        try:
            response = tavily_client.search(query=query, max_results=5)
            results = response.get("results", [])

            if not results:
                return "No results found."

            formatted_results = []
            for result in results:
                title = result.get("title", "No title")
                url = result.get("url", "")
                content = result.get("content", "")
                formatted_results.append(f"Title: {title}\nURL: {url}\nContent: {content}\n")

            return "\n---\n".join(formatted_results)
        except Exception as e:
            return f"Error searching: {str(e)}"

    return tavily_search


def create_weaviate_tool(repo: WeaviateRepository) -> Any:
    """
    Create a LangChain tool wrapper for Weaviate retrieval.

    Args:
        repo: WeaviateRepository instance

    Returns:
        LangChain tool for Weaviate retrieval
    """
    @tool
    def weaviate_retrieve(query: str) -> str:
        """
        Search internal knowledge base using Weaviate vector search.

        Use this tool when you need to find information from internal documents
        or knowledge base. This searches pre-indexed documents.

        Args:
            query: Search query string

        Returns:
            Formatted string with retrieved documents
        """
        try:
            results = repo.search(query, limit=5)

            if not results:
                return "No documents found in knowledge base."

            formatted_results = []
            for result in results:
                text = result.get("text", "")
                metadata = result.get("metadata", {})
                metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items()])
                formatted_results.append(f"Content: {text}\nMetadata: {metadata_str}\n")

            return "\n---\n".join(formatted_results)
        except Exception as e:
            return f"Error retrieving from knowledge base: {str(e)}"

    return weaviate_retrieve



