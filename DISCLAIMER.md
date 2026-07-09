# Disclaimer

This repository is a portfolio-safe slice of the AIGOS platform. It is not the full production system and does not include proprietary workflows, prompts, multi-tenant logic, credentials, or vendor integrations.

The code in this repository is real and runnable. The campaign pipeline — the stage runner, request validation, platform-restriction logic, and the service/provider wiring — executes end-to-end. External providers (LLM, research, vision, photo enhancement, storage) are deterministic mocks that stand in for the production integrations, so the pipeline runs offline with no API keys. What is intentionally excluded is documented in [`PORTFOLIO_SCOPE.md`](PORTFOLIO_SCOPE.md).

The purpose of this repository is to demonstrate architecture, code organization, and engineering approach without exposing intellectual property or sensitive production configuration.
