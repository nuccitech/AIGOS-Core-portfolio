from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CampaignRequest:
    audience: str
    channel_mix: List[str]
    goal: str
    tone: str
    constraints: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "CampaignRequest":
        return cls(
            audience=payload.get("audience", "founders at seed-stage startups"),
            channel_mix=payload.get("channel_mix", ["linkedin", "email"]),
            goal=payload.get("goal", "lead generation"),
            tone=payload.get("tone", "concise and practical"),
            constraints=payload.get("constraints", {}),
        )


@dataclass
class CampaignPlan:
    summary: str
    channels: List[str]
    key_messages: List[str]


@dataclass
class DraftContent:
    channel: str
    title: str
    body: str
