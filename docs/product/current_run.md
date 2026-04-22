# Current Run

## Active Feature
- Name: Discord Integration
- Backlog ID: B-001
- Goal: Implement a mocked-first webhook notification workflow that proves setup value before real Discord delivery.
- Operating Mode: Build

## Linked Artifacts
- Brief: docs/product/briefs/discord_integration.md
- Design Handoff: docs/product/briefs/discord_integration_design_handoff.md
- Contract: docs/product/contracts/discord_webhook.md
- Architecture: docs/product/architecture.md
- Launch Checklist: docs/ops/launch_checklist.md

## Definition Of Done
- [ ] Feature brief is current and accepted.
- [ ] Contract covers success, error, loading, and security-sensitive behavior.
- [ ] UI states are defined for configuration and validation.
- [ ] Mocked delivery path is implemented and tested.
- [ ] Launch and measurement steps are prepared.

## Active Tasks
### Product Spec
- [x] Create Discord integration feature brief.
- [x] Draft Discord webhook contract.

### Design
- [x] Define the Webhook Settings flow and state handling.

### Engineering
- [ ] Create mock handler for POST /api/webhooks.
- [ ] Build the webhook settings form with validation.
- [ ] Connect the form to the mock API.

### Growth And Ops
- [ ] Define the launch message and measurement checkpoint.

## Risks
- Webhook URLs are sensitive and must not be logged in plaintext.
- User setup friction may be higher than the value of the first release.

## Blockers
- None.