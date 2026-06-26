from typing import Any, Dict


class MockVisionService:
    """
    Portfolio mock. Production swap: VisionAnalysisService uses GPT-4V to
    return a marketing-focused description of an uploaded image.

    Real interface (see INTEGRATIONS.md):
        analyze_image(image_source, context, detail_level) -> dict
    """

    def analyze_image(
        self,
        image_source: str,
        context: str = "",
        detail_level: str = "high",
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "description": (
                "Professional work photo demonstrating quality craftsmanship. "
                "Strong visual for trust-building content."
            ),
        }
