from typing import Any, Dict, List

from webapp.models.schema import CampaignRequest, PlatformRestriction

# Proprietary compliance matrix omitted per WHAT_TO_OMIT.md.
# Production version maps industry categories to restricted platforms,
# allowed platforms, warnings, and compliance_notes injected into the AI prompt.
REGULATED_INDUSTRIES: Dict[str, Dict[str, Any]] = {
    "example_industry": {
        "restricted_platforms": ["example_platform"],
        "warning": "Content restricted on example_platform for example_industry.",
        "compliance_notes": "Focus on education; avoid health claims.",
    },
}


class PolicyService:
    def check_platform_restrictions(
        self, industry: str, target_platforms: List[str]
    ) -> PlatformRestriction:
        rules = REGULATED_INDUSTRIES.get(industry.lower(), {})
        restricted = rules.get("restricted_platforms", [])
        allowed = [p for p in target_platforms if p not in restricted]
        warnings = [
            rules.get("warning", f"{industry} restricted on {p}")
            for p in restricted
            if p in target_platforms
        ]
        return PlatformRestriction(
            allowed_platforms=allowed,
            restricted_platforms=restricted,
            warnings=warnings,
        )

    def evaluate(self, request: CampaignRequest) -> Dict[str, Any]:
        restriction = self.check_platform_restrictions(
            request.industry, request.target_platforms
        )
        return {
            "status": "restricted" if restriction.warnings else "approved",
            "allowed_platforms": restriction.allowed_platforms,
            "restricted_platforms": restriction.restricted_platforms,
            "warnings": restriction.warnings,
        }
