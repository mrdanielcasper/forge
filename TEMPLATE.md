# Solopreneur OS: Template Customization Guide

Welcome to your new Solopreneur OS! To get started, you need to replace the blank-slate business context with your actual product strategy.

## 🛑 1. Files You MUST Replace
These files dictate how your AI agents behave and what they build. Open them and overwrite the placeholder text with your own business logic:

- `docs/company/thesis.md` - Your core business mission, market, and wedges.
- `docs/company/personas.md` - Who are you building for?
- `docs/company/scorecard.md` - How do you measure success?
- `docs/company/feedback_log.md` - Your raw user feedback.
- `docs/product/backlog.md` - Your prioritized feature list.
- `docs/product/current_run.md` - The current active feature being built.

*(Tip: Delete the `# TEMPLATE: Replace with your own content` header from these files once you've fully customized them.)*

## ⚠️ 2. Files You Must UPDATE Before Launch
- `src/api/main.py` - Replace the scaffold FastAPI entry point with your actual app logic.
- `src/web/main.tsx` - Replace the scaffold React frontend entry point with your actual app logic.
- `tests/api/test_initial.py` - Replace the smoke tests with real unit tests.
- `.github/workflows/dependabot-auto-merge.yml` - (Optional) Recreate and enable auto-merge only AFTER you have real tests protecting your `main` branch.

## 🔒 3. Structural Files (Do NOT Delete)
These files are the engine of your OS. Leave them alone unless you are explicitly upgrading the OS architecture:
- `orchestrator.py` - The brain of the operation.
- `agents/*.xml` - The AI agent prompts.
- `scripts/githooks/pre-commit` - Your security bouncer.
- `docs/templates/*` - Used by the AI to generate standardized documents.
- `docs/company/lessons_learned.md` - Your system memory. (Add to this, but don't delete the global OWASP/Architecture rules).
- `docs/product/style_guide.md` - Only update the variables; do not delete the file.
- `docs/product/architecture.md` - Only update the tech stack; do not delete the file.