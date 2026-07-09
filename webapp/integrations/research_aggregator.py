from typing import Any, Dict, List


class MockResearchAggregator:
    """
    Portfolio mock. Production swap: ResearchAggregator scrapes and summarises
    web content, returning sources, parsed user_content, and a summary string.

    Production interface:
        aggregate_research(topic, industry, max_sources, recency_days,
                           include_sources, user_urls) -> dict
    """

    def aggregate_research(
        self,
        topic: str,
        industry: str,
        max_sources: int = 5,
        recency_days: int = 30,
        include_sources: List[str] = None,
        user_urls: List[str] = None,
    ) -> Dict[str, Any]:
        user_urls = user_urls or []
        sources = [f"[mock-fetch] {url}" for url in user_urls]
        enhanced_context = (
            f"Topic: {topic}. Industry: {industry}. "
            f"Reviewed {len(sources)} user-supplied source(s)."
        )
        return {
            "sources": sources,
            "user_content": {},
            "summary": enhanced_context,
            "enhanced_context": enhanced_context,
        }
