# Solopreneur OS 🏭

An autonomous, local-first AI software factory that builds verifiable, zero-debt React + FastAPI applications.

Unlike generic coding assistants, Solopreneur OS operates as a strict assembly line. It breaks software development down into five distinct AI personas, forces them to write their own documentation, and strictly executes Test-Driven Development (TDD) before moving to production.

---

## ⚠️ Template Customization Checklist
Before deploying this OS to production, you must complete the following:
- [ ] **Customize the Business Logic:** Read `TEMPLATE.md` to see which documents in the `docs/` folder you must overwrite with your own business logic.
- [ ] **Write Real Tests:** The current `tests/api/test_initial.py` and `tests/web/a11y.e2e.ts` files are structural smoke tests. Do not rely on CI until real tests are written for your app.
- [ ] **Replace Scaffold Entrypoints:** Overwrite the stub `src/api/main.py` and `src/web/main.tsx` files with your actual application logic.

## 🚀 First Time Setup

1. **Environment Variables:** Copy `.env.example` to `.env` and add your API keys.
2. **Backend Dependencies:** We use `uv` for lightning-fast, deterministic package management.
   ```bash
   # Install uv if you don't have it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Sync the locked dependencies (creates .venv automatically)
   uv sync
   ```
3. **Frontend Dependencies (JS/TS):** We use npm to lock in our strict linting, testing, and UI tools.
   ```bash
   # Install Biome, Vitest, Playwright, and base React dependencies
   npm install
   ```
4. **Activate the Pre-Commit Bouncer:** This native Git hook prevents the AI from leaking secrets or faking test results.
   ```bash
   git config core.hooksPath scripts/githooks
   ```
5. **Boot the Factory:**
   ```bash
   uv run python orchestrator.py "What should we build first?" --os-verbose
   ```

---

## 🧠 The 6-Node Architecture

The OS is driven by a deterministic Python script (`orchestrator.py`) that acts as your Chief of Staff, routing tasks to 5 specialized LLM agents defined in the `agents/` folder.

1. **The Orchestrator (`orchestrator.py`):** A deterministic Python router. It parses routing tags, aggressively prunes context to save tokens, manages the multi-agent execution queue, and dynamically routes tasks to the most cost-effective LLM provider (`SMART_ROUTING`).
2. **Strategy (`strategy.xml`):** The business filter. Evaluates ideas based on Cost of Delay, Reversibility (1-Way vs 2-Way doors), Legal/Compliance risk, and Strategic Sourcing (Build vs. Buy vs. OSS). 
3. **Product Spec (`product_spec.xml`):** The architect's radar. Turns strategy into strict Feature Briefs and Data Contracts. Identifies when an idea crosses a system boundary and triggers an Architectural Decision Record (ADR).
4. **Design (`design.xml`):** The visual mapper. Generates Mermaid.js state flows and defines WCAG-compliant, atomic UI components using utility-first CSS, driven by the `style_guide.md`.
5. **Engineering (`engineering.xml`):** The builder & janitor. Drafts ADRs for your approval, writes Interfaces/Mocks first, executes TDD (Red-Green-Harden), runs linters, integrates `shadcn/ui` components, and ruthlessly deletes dead code during Teardowns. 
6. **Growth/Ops (`growth_ops.xml`):** The privacy officer and analyst. Enforces compliance, defines infrastructure "Kill Switches" (e.g., alert thresholds), evaluates strict A/B or Pre/Post cohorts, and commands Teardowns.

---

## 👤 The Operator's Role (Human-in-the-Loop)

You are the CEO, the lead investor, and the final decision-maker. You **do not** write code or draft specs. Your job is to:
1. **Provide raw signals:** Feed user pain points into the prompt.
2. **Approve Architecture:** When the pipeline pauses with `ADR_STATE: [Pending Human]`, you read the drafted ADR in `docs/product/adr/` and change its status to "Accepted".
3. **Provide Raw Data:** When Growth/Ops asks for launch metrics, you paste the raw numbers from your dashboard (Datadog, PostHog, etc.).
4. **Curate the Memory:** Update `docs/company/lessons_learned.md` when an agent makes a mistake, ensuring it never happens twice.

---

## 📁 Repository Structure & Canonical Documents

```text
.github/
  workflows/ci.yml    # Enterprise-grade CI testing & TruffleHog Secret Scanning
  dependabot.yml      # Supply chain vulnerability scanner
src/
  api/                # Backend Sandbox (FastAPI / Python)
    Dockerfile        # Production multi-stage build container
  web/                # Frontend Sandbox (React / Vite / TS / Shadcn)
tests/
  api/                # Pytest & BDD Feature files
  web/                # Vitest & Playwright E2E files
docs/                 # Global OS memory, ADRs, Contracts, and Strategy
  product/
    style_guide.md    # Canonical visual brand rules
agents/               # The LLM prompt definitions
scripts/
  githooks/
    pre-commit        # The automated local security/lint bouncer
orchestrator.py       # The execution engine
pyproject.toml        # Backend dependencies & Ruff/Pytest config
package.json          # Frontend dependencies & scripts
components.json       # Shadcn UI component routing configuration
biome.json            # JS/TS Linting & Formatting config
vite.config.ts        # Frontend build & test config
tailwind.config.js    # Utility-first CSS design tokens
postcss.config.js     # CSS processing bridge
playwright.config.ts  # End-to-End browser testing config
```

---

## 🏗️ Infrastructure & Continuous Integration

This OS is built on a strict **"Git Push to Deploy"** PaaS (Platform-as-a-Service) model:
* **Zero Custom Cloud-Formation:** We explicitly ban complex orchestrators (Kubernetes, Terraform) to avoid maintenance debt. 
* **Backend:** Handled by a single highly optimized `Dockerfile` in `src/api/` intended for Render or Railway.
* **Frontend:** Deployed instantly via Vercel or Netlify directly from the `src/web/` directory.
* **Security & CI Gate:** All commits pushed to `main` trigger GitHub Actions. This pipeline runs Ruff (SAST), Biome, Pytest, Vitest, Playwright (E2E & A11y), and TruffleHog (Verified Secret Scanning). **Only green builds are deployed.**

---

## 🎨 Design System & Headless Components

The OS utilizes **Code as the Design Kit**. There is no Figma. 
* **The Visual Style Guide:** Located at `docs/product/style_guide.md`, this dictates spacing, vibe, and semantic colors.
* **Shadcn/UI:** The Engineering agent generates accessible, un-styled Radix components on the fly (via `components.json`) directly into the `src/web/components/ui/` folder.
* **Tailwind CSS:** Components are styled using the strict semantic variables locked into `tailwind.config.js` and `index.css`.

---

## 🛠️ How To Prompt the OS

The Orchestrator listens to specific syntax tags in your prompt to allow you to "steer" the factory.

### 1. The Standard Run (New Features)
To start a brand new feature from scratch, simply talk to the Strategy agent.
```bash
uv run python orchestrator.py "Let's build a Waitlist landing page to capture emails before launch." --os-verbose
```
*The Orchestrator wakes up Strategy -> Spec -> Engineering (ADR Draft) -> [PAUSE FOR YOUR APPROVAL] -> Engineering (Build) -> Ops.*

### 2. The CEO Override (Targeted Starts)
If you already know exactly what you want and want to skip the Strategy agent, use the `[START: AgentName]` tag. This injects your prompt directly into that specific agent's brain.
```bash
uv run python orchestrator.py "[START: Engineering] The CEO has updated the styling guidelines. Re-write the Waitlist UI to use the new brand colors."
```
*Valid agents: Strategy, Product Spec, Design, Engineering, Ops.*

### 3. The Hotfix (Bug Squashing)
If your application breaks, use the `[HOTFIX]` tag. This bypasses all PM/Design steps, wakes up the Engineering agent immediately, and forces it to fix the code.
```bash
uv run python orchestrator.py "[HOTFIX] The /api/waitlist route is throwing a 500 internal server error when the email is missing."
```

### 4. The Teardown (Removing Tech Debt)
AI codebases accumulate dead code. To safely delete a feature, use the `[TEARDOWN]` tag. The OS will trace the feature's dependencies and surgically remove it without breaking the rest of the app.
```bash
uv run python orchestrator.py "[TEARDOWN] We are pivoting. Remove the Waitlist feature from the frontend and backend."
```

---

## 🔒 Security & Architecture

Solopreneur OS is built for local execution and maximum data integrity.

* **Context Funneling:** The OS actively parses `current_run.md` to only load the exact files relevant to the active feature. This prevents O(N) token scaling issues as your codebase grows.
* **Non-Destructive Logging:** Tracking files like `experiment_log.md` use a specialized `append_to_file` tool to ensure the AI never accidentally overwrites your historical database.
* **Component RAG:** The Engineering and Design agents are dynamically fed a list of your existing `src/web/components/ui/` files so they never hallucinate imports.
* **The Sandbox:** The Orchestrator intercepts all shell commands. It only allows safe commands like `uv run pytest`, `npm run test`, and linting. It actively blocks shell injection and restricted path traversals.

---

## ⚖️ Do's and Don'ts

* **DO use `lessons_learned.md`:** If an agent hallucinates a Tailwind class or uses an outdated library, add a bullet point here.
* **DO let the pre-commit hook work:** If `git commit` fails, do not bypass it. Use the `[HOTFIX]` command and force the AI to fix its own mess.
* **DON'T bypass the ADR process:** Never let agents arbitrarily decide to add Postgres or Redis without your explicit "Accepted" stamp.
* **DON'T let agents write to `architecture.md`:** Only the Engineering agent is allowed to update this file, and only *after* an ADR is accepted.
* **DON'T bloat the backlog:** Strategy will actively try to kill bad ideas. Let it.

## 💡 Helpful Tips

* **Smart Routing:** Keep `SMART_ROUTING=true` in your `.env`. The Orchestrator automatically routes logic-heavy tasks (Strategy) to deep-reasoning models (like `o4-mini`), and coding tasks to standard models (like `claude-sonnet-4-5`).
* **Context Pruning:** The Orchestrator uses deterministic pruning (`tail_file`) to only send the most recent logs to the AI, saving you massive API costs.