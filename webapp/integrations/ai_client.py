from typing import Dict, List


class MockAIClient:
    def generate(self, prompt: str) -> Dict[str, List[str]]:
        return {
            "prompt_used": prompt,
            "messages": [
                "Example output: Draft a short LinkedIn post introducing a new product.",
                "Example output: Draft a follow-up email summarizing benefits.",
            ],
        }
