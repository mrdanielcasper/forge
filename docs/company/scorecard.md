# Scorecard

## North Star Metric
- Weekly successful workflow completions per active customer.

## Current Operating Focus
- Primary goal: prove that users will configure and repeat a chat-adjacent workflow alert.
- Current wedge: Discord webhook setup and confirmation.

## Metrics
| Metric | Definition | Target | Why It Matters |
| :--- | :--- | :--- | :--- |
| Activation | Percentage of new users who configure one working alert flow within 7 days. | 40%+ | Proves the setup is understandable and worth doing. |
| Repeat Usage | Percentage of activated users who trigger or review the workflow again the following week. | 50%+ | Distinguishes curiosity from habit. |
| Time Saved | Estimated minutes of manual follow-up removed per successful workflow. | 10+ minutes | Ties product value to operational relief. |
| Reliability | Percentage of workflow runs that complete without avoidable user-facing failure. | 95%+ in mocked path | Builds trust in the core job. |
| Revenue Readiness | Percentage of active users who reach a point where paid value is obvious. | Qualitative for now | Helps avoid shipping a habit with no commercial path. |

## Review Cadence
- Weekly: activation, repeat usage, reliability, and top feedback themes.
- Monthly: time saved, revenue readiness, and whether the wedge still looks strategically correct.

## Decision Rules
- Build only when a feature has a clear path to improving activation, repeat usage, reliability, or time saved.
- If a feature does not support the current wedge, park it unless there is direct evidence of stronger demand.
- If setup friction stays high while repeat usage stays low, simplify or kill the workflow rather than layering on more features.
- If users ask for broader automation before the core workflow is repeatedly used, capture the signal but do not expand scope by default.

## Current Questions
- Will users trust a mocked-first setup flow enough to complete it?
- Is Discord the right first environment, or just the easiest place to prototype the workflow?
- Does visible confirmation of completion matter more than deeper automation in the first release?