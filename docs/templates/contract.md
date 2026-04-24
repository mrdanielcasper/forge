# Feature Contract Template

**Status:** Draft
**Version:** 0.1.0
**Owning Brief:** `docs/product/briefs/[feature_name].md`

## 🏗️ Architectural Impact
- **ADR Radar:** [Needed / None] (Explain why if needed)

## Functional Summary
- What triggers the behavior?
- What does success look like from the user's perspective?

## Non-Goals
- What is intentionally out of scope for this specific contract to protect scope?

## Interface & Schema
- Request shape, command, event, or data exchange definition.

## Success Response Or Outcome
- Show the expected success payload or state transition.

## Error Responses
- List meaningful failure modes and how they differ.

## UI States (Mapped to Blueprint)
- Loading
- Empty
- Success
- Error

## Permissions And Security
- Who can perform the action?
- What sensitive data must be masked or protected?

## Analytics Events
- What telemetry events must be triggered for learning, compliance, or monitoring?

## Rollout & Rollback Plan
- **Rollout:** How should this ship safely? (e.g., feature flags, beta cohorts)
- **Rollback:** Exactly how to undo this feature if it fails in production (e.g., downgrade database migrations, flip feature flag).