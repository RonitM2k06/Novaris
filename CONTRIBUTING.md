# Contributing to Novaris

We welcome contributions from economists, data scientists, and engineers to expand the Novaris Digital Twin!

## Getting Started

1. Fork the repository.
2. Clone your fork locally.
3. Set up the Python backend (`.venv`) and the Next.js frontend (`web`).
4. Run `python scripts/seed_demo.py` to get the baseline dataset.
5. Create a feature branch.

## Areas for Contribution
* **Ontology Expansion:** Adding new nodes (e.g., Geopolitics, Supply Chain).
* **Calibration Algorithms:** Improving the cross-correlation metrics or VAR implementations.
* **Frontend:** Hooking up the FastAPI endpoints to the Next.js Command Center.

## Pull Request Process
1. Ensure `npm run build` succeeds in the `web/` directory.
2. Ensure no linting errors exist in the Python code.
3. Update the `CHANGELOG.md`.
4. Submit PR for review.
