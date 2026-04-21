# Solo Software Company OS

This repository is a lightweight operating system for building a one-person software company. It is designed to keep strategy, product definition, design, engineering, and launch work tied to durable artifacts instead of ad hoc chat history.

## First Time Setup
1. Copy `.env.example` to `.env` and add your API keys.
2. Run `git config core.hooksPath scripts/githooks` to activate the AI safety nets.

## What This Repo Is For
- Turning raw customer pain into testable opportunities.
- Converting validated opportunities into scoped product briefs and contracts.
- Keeping active delivery work tied to a single current run.
- Closing the loop from launch back into measurement and feedback.

## Operating Model
The repo is organized around a simple flow:

1. Strategy identifies a painful job worth solving.
2. Product Spec turns that opportunity into a feature brief and contract.
3. Design defines the user flow and state handling.
4. Engineering implements from the brief and contract.
5. Growth/Ops handles launch, measurement, and learning.

The skills in the `skills/` folder exist to reinforce this sequence. They are useful only if the documents they depend on are real and current.

## Repository Structure
```text
docs/
  company/
    thesis.md
    personas.md
    scorecard.md
    feedback_log.md
  product/
    backlog.md
    current_run.md
    architecture.md
    briefs/
    contracts/
    adr/g
  ops/
    launch_checklist.md
    experiment_log.md
  templates/
    feature_brief.md
    contract.md
    adr.md

skills/
  orchestrator.xml
  strategy.xml
  product_spec.xml
  design.xml
  engineering.xml
  growth_ops.xml
```

## Canonical Documents
- `docs/company/thesis.md`: the business thesis and strategic wedge.
- `docs/company/personas.md`: who the product is for and who it is not for.
- `docs/company/scorecard.md`: the metrics that justify building.
- `docs/company/feedback_log.md`: raw evidence from users and operations.
- `docs/product/backlog.md`: prioritized opportunities with evidence and target metrics.
- `docs/product/current_run.md`: the single active delivery record.
- `docs/product/briefs/`: live feature briefs.
- `docs/product/contracts/`: live contracts for feature behavior and interfaces.
- `docs/ops/launch_checklist.md`: launch readiness and review criteria.
- `docs/ops/experiment_log.md`: outcome tracking and decisions.

## How To Use It
### When you have a new idea
- Start with `docs/company/feedback_log.md` if it comes from a user signal.
- Use `skills/strategy.xml` to test whether the idea maps to a painful job and a metric.
- Add or refine the item in `docs/product/backlog.md` only when there is evidence.

### When an idea is ready to define
- Use `skills/product_spec.xml`.
- Create a live brief under `docs/product/briefs/` from `docs/templates/feature_brief.md`.
- Create a live contract under `docs/product/contracts/` if the work crosses a UI or service boundary.
- Move the work into `docs/product/current_run.md` only after the brief exists.

### When work is ready to build
- Use `skills/design.xml` for flow and state handling.
- Use `skills/engineering.xml` for acceptance scenarios, tests, implementation, and delivery updates.
- Keep `docs/product/current_run.md` current as the source of truth.

### When work is ready to ship
- Use `skills/growth_ops.xml`.
- Update `docs/ops/launch_checklist.md` with the target message, metric, and review date.
- Record what happened in `docs/ops/experiment_log.md` and feed user reactions back into `docs/company/feedback_log.md`.

## Current Focus
The active example in this repo is Discord Integration:
- Backlog item: `B-001`
- Brief: `docs/product/briefs/discord_integration.md`
- Contract: `docs/product/contracts/discord_webhook.md`
- Current run: `docs/product/current_run.md`

This is intentionally a mocked-first workflow. The goal is to validate setup value and user understanding before investing in a fuller production integration.

## Rules That Matter
- Do not build from raw ideas when a brief or contract is missing.
- Do not treat the backlog as a dumping ground; every item needs pain, evidence, and a metric.
- Do not let active work live anywhere except `docs/product/current_run.md`.
- Do not launch without a measurement plan and review date.

## Recommended Working Rhythm
1. Capture signals in feedback.
2. Turn repeated pains into experiments.
3. Turn validated experiments into feature briefs.
4. Build only from current-run artifacts.
5. Review metrics and write down what changed.

## Founder Workflow
### Weekly Review
- Read `docs/company/feedback_log.md` and pull out repeated pains.
- Review `docs/company/scorecard.md` against the last week's actual signals.
- Decide whether the current wedge still deserves the next week of effort.
- Clean up `docs/product/backlog.md` so only evidence-backed work stays near the top.

### Starting New Work
- If the idea is not tied to a real pain, do not spec it.
- If the pain is real but the solution is unclear, run Strategy and log an experiment.
- If the opportunity is validated enough to define behavior, create a brief and contract before moving it into the current run.

### During Active Delivery
- Keep `docs/product/current_run.md` current.
- Treat briefs, contracts, and design handoffs as the source of truth for behavior.
- Avoid broadening scope mid-run unless the new requirement changes the core job to be done.

### After Shipping
- Update `docs/ops/launch_checklist.md` with what actually launched.
- Record the outcome in `docs/ops/experiment_log.md`.
- Add real user feedback back into `docs/company/feedback_log.md`.
- Decide explicitly whether to expand, iterate, or kill the feature.

If this repo starts feeling heavy, cut process rather than adding more. The point is to preserve clarity, not simulate a larger company.