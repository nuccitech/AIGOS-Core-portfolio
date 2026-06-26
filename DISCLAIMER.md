# Disclaimer

This repository is a portfolio-safe slice of the AIGOS platform. It is not the full production system and does not include proprietary workflows, prompts, multi-tenant logic, credentials, or vendor integrations.

The code in this repository is real and runnable. The campaign pipeline executes end-to-end against a real OpenAI call when `OPENAI_API_KEY` is set, and falls back to a deterministic template otherwise — no stage is stubbed out or faked. What is intentionally excluded is documented in [`PORTFOLIO_SCOPE.md`](PORTFOLIO_SCOPE.md).

The purpose of this repository is to demonstrate architecture, code organization, and engineering approach without exposing intellectual property or sensitive production configuration.
