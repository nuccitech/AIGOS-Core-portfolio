from dataclasses import dataclass
from typing import Dict


@dataclass
class PolicyDecision:
    status: str
    reason: str


    @classmethod
    def from_dict(cls, payload: Dict[str, str]) -> "PolicyDecision":
        return cls(status=payload.get("status", "unknown"), reason=payload.get("reason", ""))
