# Teardown Manifest: [Feature Name]

**Status:** Pending Execution
**Experiment Log:** `docs/ops/experiment_log.md`

## 🪦 Reason for Termination
[Explain why this feature was killed (e.g., "Failed A/B test", "High setup friction, 0% retention").]

## 🗑️ Code Deletion Targets
### Frontend (`src/web/`)
- [ ] Delete Route/Pages: `...`
- [ ] Delete UI Components: `...`
- [ ] Remove from Navigation/Sidebar.

### Backend (`src/api/`)
- [ ] Delete Endpoints/Routers: `...`
- [ ] Delete Database Models/Migrations: `...`

## 🧹 Telemetry & Content Cleanup
- [ ] Remove all associated strings from `src/web/lib/content.ts`.
- [ ] Remove tracking events from the analytics schema.

## 🏗️ Architectural Rollback
- [ ] **Infrastructure:** Did this feature require a 3rd-party service or database addition in an ADR? If yes, remove the dependency.
- [ ] **Dependencies:** Run `npm uninstall [package]` or `uv remove [package]` for any libraries strictly associated with this feature.