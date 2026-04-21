# Current Run: Discord Integration (B-001)
**Goal:** Implement a mocked-first webhook notification system.

## 📋 Definition of Done (DoD)
- [ ] Contract.md signed off by PM.
- [ ] UI Components (Visual Architect) implemented in Tailwind.
- [ ] Backend logic mocked via MSW/Handlers.
- [ ] 100% Test coverage on the "Send Alert" function.

## 🛠 Active Tasks
### Phase 1: Design & Contract
- [x] Draft `docs/contracts/discord_webhook.md`
- [ ] Design the "Webhook Settings" panel (Visual Architect)

### Phase 2: Mocked Build (Nexus-Zero)
- [ ] Create mock server handlers for `POST /api/webhooks`
- [ ] Build UI form with validation (Happy/Edge paths)
- [ ] Connect form to Mock API

### Phase 3: Hardening
- [ ] Implement actual Discord API integration (Flip the switch)
- [ ] Security Audit: Ensure Webhook URLs aren't logged in plaintext.

## 🛑 Blockers
- None.