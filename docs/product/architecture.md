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