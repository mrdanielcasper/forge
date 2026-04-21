# Product Architecture

## Principles
- Keep the system narrow, testable, and easy to change.
- Separate domain logic from transport, storage, and UI details.
- Favor mocked-first delivery for new workflows until demand is proven.

## Core Boundaries
- Product decisions live in briefs and contracts, not only in code comments.
- UI concerns should be separated from workflow and integration logic.
- External services such as Discord should be wrapped behind explicit interfaces.

## Non-Negotiables
- Sensitive values must not be logged in plaintext.
- Error states must be explicit in both the product contract and implementation.
- Active delivery work must be tracked in docs/product/current_run.md.

## ADR Trigger
Create an ADR when a change affects system boundaries, external integrations, or long-term maintenance cost.

## Tooling & Execution Stack
- **Backend Framework:** Python / FastAPI
- **Frontend Framework:** TypeScript / Vite / React / Tailwind
- **Python Linting & Testing:** `uv` for packages, `ruff` for lint/format, `pytest` + `pytest-bdd` for testing.
- **JS/TS Linting & Testing:** `npm` for packages, `Biome` for lint/format, `Vitest` for unit tests, `Playwright` for E2E.
- *Constraint:* The Engineering agent MUST use these tools. Do not install or configure ESLint, Prettier, Jest, Black, Flake8, Django, or Webpack.