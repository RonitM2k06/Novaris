# Novaris GitHub Release Sprint (Implementation Plan)

This plan outlines the steps to prepare Novaris as a research-grade open-source project, focusing exclusively on repository credibility, comprehensive documentation, and structural polish.

## User Review Required

> [!IMPORTANT]
> **Image Generation Strategy**
> The sprint requires generating screenshots for `docs/screenshots/` (Command Center, Scenario Studio, etc.). Since I do not have a headless browser to natively screenshot the running Next.js application, I will use my `generate_image` tool to synthesize highly realistic mockups of the Ultra Dark Command Center interface based on the UI we just built. Is this acceptable for the release sprint?

## Proposed Execution Plan

### Phase 1: Brutal Audit
* Conduct a repository-wide file traversal.
* Document unused variables, missing types, placeholder mock data in `web/`, and Python linter errors.
* Output findings to `NOVARIS_FINAL_AUDIT.md`.

### Phase 2: World-Class README
* Write a comprehensive, multi-section `README.md` at the project root.
* Include Mermaid DAG diagrams visualizing the expanded Economic Ontology.
* Format as an academic/engineering hybrid document detailing methodology, validation results, and installation instructions.

### Phase 3: Screenshot Generation
* Use the `generate_image` tool to synthesize 6 ultra-dark, mission-control style application screenshots.
* Save them into `docs/screenshots/` and embed them correctly into the new README.

### Phase 4: Demo Dataset
* Create `scripts/seed_demo.py` utilizing the fallback dataset generation logic we built in Phase 4.
* Ensure it outputs a pre-populated SQLite database or CSV suite so fresh clones have immediate, usable macroeconomic time-series data covering 2008, COVID, and 2022.

### Phase 5: Research Documentation
* Create a `docs/` folder.
* Synthesize all prior phase artifacts (`calibration_report`, `historical_replay_report`, etc.) into consolidated, academic-grade markdown files:
  * `research_report.md`
  * `methodology.md`
  * `architecture.md`
  * `validation_results.md`

### Phase 6: OSS Polish
* Generate standard Open Source repository files:
  * `LICENSE` (MIT)
  * `CONTRIBUTING.md`
  * `ROADMAP.md`
  * `CHANGELOG.md`
  * `CODE_OF_CONDUCT.md`

### Phase 7 & 8: Release Readiness
* Final verification of `npm run build` and Python dependencies.
* Generate the `NOVARIS_RELEASE_REPORT.md` scoring the repository's readiness across Documentation, Research Quality, and Engineering Quality.

## Verification Plan
* Run `npm run build` in `web/` to ensure no frontend breaks occurred.
* Execute `python scripts/seed_demo.py` to verify the demo data populates without errors.
* Ensure all markdown internal links and image links resolve correctly in the README.
