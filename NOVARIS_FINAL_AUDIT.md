# Novaris Final Codebase Audit

> [!CAUTION]
> **Audit Status:** PENDING CRITICAL FIXES. This repository is not yet ready for public distribution. It requires major architectural de-mocking and environment cleanup before a GitHub Push.

## Critical Issues

1. **Frontend Disconnected from Backend (Architecture Inconsistency):** 
   The Next.js Command Center (`web/`) is a visual shell. It does not actually communicate with the Python backend (`api.py`). The `ScenarioStudio`, `HistoricalReplay`, and `OntologyExplorer` components all use hardcoded mock data. Releasing this as a "Digital Twin" would immediately destroy repository credibility when users realize the UI isn't executing real mathematics.
2. **Environment-Specific Hardcoding:** 
   In `src/api.py`, the `get_reports()` endpoint uses a hardcoded, user-specific absolute path (`C:\Users\ronit\.gemini\antigravity\...`) to read markdown files. This will instantly crash on any other developer's machine.
3. **Missing Dependency Management:** 
   There is no `requirements.txt` or `pyproject.toml` in the Python root. Users cloning the repository have no way to reproduce the backend environment (which relies on `pandas`, `scipy`, `fastapi`, `uvicorn`, etc.).

## Medium Issues

1. **Placeholder Proxy Datasets:** 
   In `novaris/data.py`, the `DataFetcher` falls back to `_generate_fallback_data()` when FRED times out. This function generates synthetic math data instead of using a cached local CSV. This undermines the "Real Data Calibration" claim if the user experiences network issues.
2. **Missing `docs/screenshots`:** 
   The README and documentation will appear broken until actual screenshots are populated into the expected `docs/screenshots/` directory.
3. **Unused Code:**
   The `test_*.py` files scattered in the `src/` directory act as execution scripts rather than actual unit tests. They should be moved to an `examples/` or `scripts/` folder for clarity, leaving `tests/` for actual pytest suites.

## Minor Issues

1. **TypeScript Warnings:** 
   In `web/src/store/workspace.ts` and UI components, `any` types are used for `contextData` instead of strict interfaces.
2. **Missing Linting Configs:** 
   The Python backend lacks a `.flake8` or `mypy.ini` configuration to enforce code quality.
3. **Missing Ignored Files:**
   There is no `.gitignore` file, meaning the `.venv`, `.next`, and `__pycache__` directories will be accidentally committed to GitHub if not careful.
