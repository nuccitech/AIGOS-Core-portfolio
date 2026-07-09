from typing import Any, Dict, Optional


class MockLLMClient:
    """Portfolio mock. Production swap: TrackedOpenAI wrapping openai.ChatCompletion."""

    def generate_post(
        self,
        topic: str,
        content_type: str,
        platform: str,
        tone: str,
        research_context: str,
        photo_description: str = "",
    ) -> Dict[str, str]:
        photo_note = f" Featuring: {photo_description}." if photo_description else ""
        return {
            "caption": (
                f"[{platform.upper()}] {topic} — {content_type} draft.{photo_note}"
            ),
            "content": (
                f"Example {content_type} for {platform} about {topic}. "
                f"Tone: {tone}. Research applied: {len(research_context)} chars."
            ),
        }

    def generate_hashtags(self, topic: str, niche: str) -> str:
        base = topic.lower().replace(" ", "")
        niche_tag = niche.lower().replace(" ", "")
        return f"#{base} #{niche_tag} #marketing #content #growth"
