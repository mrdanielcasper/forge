## 🚀 Feature / Fix Summary
[Briefly describe what this PR accomplishes.]

## 🔗 Artifact Links
- **Brief:** [Link to `docs/product/briefs/...`]
- **Contract:** [Link to `docs/product/contracts/...`]

## 🏗️ Architectural Impact
- [ ] No structural changes.
- [ ] ADR Accepted: [Link to `docs/product/adr/...`]

## 🧪 Pre-Flight & Verification Checklist
- [ ] `pre-commit` hook passed locally (Secret Scan, Ruff, Biome).
- [ ] Backend tests passed (`pytest`).
- [ ] Frontend tests passed (`Vitest` / E2E).
- [ ] **Accessibility tests passed (`@axe-core/playwright`).**
- [ ] ZERO raw secrets or API keys hardcoded.
- [ ] Telemetry events added to schema (if applicable).
- [ ] Visual placeholders used (No raw hallucinated SVGs).
- [ ] Environment variables updated in `.env.example` and target PaaS.

## ⚠️ Rollout Notes
- [ ] Database migrations generated and verified (if applicable).
- [ ] Feature flags or routing rules configured (if applicable).
- Additional Notes: [Any manual steps required during deployment?]

## 🗑️ Teardown (If Applicable)
- [ ] Dead code, unused UI components, and obsolete tests deleted.
- [ ] Dead telemetry events removed.