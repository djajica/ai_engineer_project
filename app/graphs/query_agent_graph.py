from __future__ import annotations

import re
from typing import Literal, TypedDict

from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, START, StateGraph

from app.ai.tools import create_tavily_tool, create_weaviate_tool
from app.repositories.weaviate_repository import WeaviateRepository


class QueryState(TypedDict, total=False):
    """State for the query agent graph."""

    query: str
    context: list[str]
    sources: list[str]
    response: str
    use_weaviate: bool


class QueryAgentGraph:
    """LangGraph agent for query processing with RAG and web search."""

    def __init__(
        self,
        anthropic_api_key: str,
        tavily_api_key: str | None,
        weaviate_repo: WeaviateRepository,
    ) -> None:
        """
        Initialize the query agent graph.

        Args:
            anthropic_api_key: Anthropic API key for Claude
            tavily_api_key: Tavily API key for web search (optional)
            weaviate_repo: WeaviateRepository instance
        """
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=anthropic_api_key,
            temperature=0.7,
        )
        self.weaviate_repo = weaviate_repo
        self.tavily_api_key = tavily_api_key

        # Create tools
        tools = [create_weaviate_tool(weaviate_repo)]
        if tavily_api_key:
            tools.append(create_tavily_tool(tavily_api_key))

        self.llm_with_tools = self.llm.bind_tools(tools)

        # Build graph
        graph = StateGraph(QueryState)
        graph.add_node("router", self.router_node)
        graph.add_node("retrieve", self.retrieve_node)
        graph.add_node("search", self.search_node)
        graph.add_node("generate", self.generate_node)

        graph.add_edge(START, "router")
        graph.add_conditional_edges(
            "router",
            self.route_decision,
            {
                "weaviate": "retrieve",
                "tavily": "search",
            },
        )
        graph.add_edge("retrieve", "generate")
        graph.add_edge("search", "generate")
        graph.add_edge("generate", END)

        self.graph = graph.compile()

    def router_node(self, state: QueryState) -> QueryState:
        """
        Router node: decides whether to use Weaviate or Tavily.

        Simple heuristic: if query mentions "recent", "latest", "current", "news",
        or "today", use Tavily. Otherwise, Weaviate.
        """
        query = state.get("query", "").lower()
        web_keywords = [
            "recent",
            "recently",
            "latest",
            "breaking",
            "current",
            "news",
            "update",
            "updated",
            "trend",
            "trending",
            "today",
            "now",
            "release",
            "announcement",
            "2024",
            "2025",
            "2026",
        ]

        use_weaviate = not any(keyword in query for keyword in web_keywords)

        return {
            **state,
            "use_weaviate": use_weaviate,
            "context": [],
            "sources": [],
        }

    def route_decision(self, state: QueryState) -> Literal["weaviate", "tavily"]:
        """Conditional routing based on router decision."""
        if state.get("use_weaviate", True):
            return "weaviate"
        return "tavily"

    async def retrieve_node(self, state: QueryState) -> QueryState:
        """Retrieve documents from Weaviate."""
        query = state.get("query", "")
        results = self.weaviate_repo.search(query, limit=5)

        context_parts = []
        sources = []

        for result in results:
            text = result.get("text", "")
            metadata = result.get("metadata", {})
            context_parts.append(text)
            # Extract source from metadata if available
            if "url" in metadata:
                sources.append(metadata["url"])
            elif "source" in metadata:
                sources.append(metadata["source"])

        return {
            **state,
            "context": context_parts,
            "sources": sources,
        }

    async def search_node(self, state: QueryState) -> QueryState:
        """Search the web using Tavily."""
        query = state.get("query", "")

        if not self.tavily_api_key:
            return {**state, "context": ["Tavily search not available."]}

        tavily_tool = create_tavily_tool(self.tavily_api_key)
        result = tavily_tool.invoke({"query": query})
        context_parts = [result] if result else []
        
        # Extract URLs from Tavily result (they're in the formatted string)
        sources = []
        if result:
            # Simple extraction - URLs are in the formatted result
            urls = re.findall(r'URL: (https?://[^\s]+)', result)
            sources.extend(urls)

        return {
            **state,
            "context": context_parts,
            "sources": sources,
        }

    async def generate_node(self, state: QueryState) -> QueryState:
        """Generate final response using Claude with context."""
        query = state.get("query", "")
        context = state.get("context", [])

        # Build context string
        context_str = "\n\n".join(context) if context else "No additional context available."

        # Create prompt
        prompt = f"""You are a helpful AI assistant. Answer the user's question using the provided context.

Context:
{context_str}

User Question: {query}

Provide a clear, accurate answer based on the context. If the context doesn't contain enough information, say so."""

        # Generate response
        response = await self.llm.ainvoke(prompt)
        answer = response.content if hasattr(response, "content") else str(response)

        return {
            **state,
            "response": answer,
        }

    async def run(self, query: str) -> QueryState:
        """
        Execute the query agent graph.

        Args:
            query: User query string

        Returns:
            Final state with response and sources
        """
        initial_state: QueryState = {"query": query}
        result = await self.graph.ainvoke(initial_state)
        return result

