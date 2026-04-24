# Solo Software Company OS

This repository is a lightweight, fully autonomous operating system for building and scaling a one-person software company. It replaces ad-hoc chat interfaces with a strict, deterministic agent pipeline designed to protect a solo founder's most precious resources: **Time, Focus, IP, and Capital.**

By tying Strategy, Product Definition, Design, Engineering, and Launch Operations to durable markdown artifacts, this OS prevents architectural bloat, ensures legal/compliance safety, and maintains a "Zero-Debt" codebase.

## 🚀 First Time Setup

1. **Environment Variables:** Copy `.env.example` to `.env` and add your API keys.
2. **Backend Dependencies:** We use `uv` for lightning-fast, deterministic package management.
   ```bash
   # Install uv if you don't have it
   curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
   
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

## 🧠 The 6-Node Architecture

The OS is driven by a deterministic Python script (`orchestrator.py`) that acts as your Chief of Staff, routing tasks to 5 specialized LLM agents defined in the `skills/` folder.

1. **The Orchestrator (`orchestrator.py`):** A deterministic Python router. It parses routing tags, aggressively prunes context to save tokens, manages the multi-agent execution queue, and dynamically routes tasks to the most cost-effective LLM provider (`SMART_ROUTING`).
2. **Strategy (`strategy.xml`):** The business filter. Evaluates ideas based on Cost of Delay, Reversibility (1-Way vs 2-Way doors), Legal/Compliance risk, and Strategic Sourcing (Build vs. Buy vs. OSS). 
3. **Product Spec (`product_spec.xml`):** The architect's radar. Turns strategy into strict Feature Briefs and Data Contracts. Identifies when an idea crosses a system boundary and triggers an Architectural Decision Record (ADR).
4. **Design (`design.xml`):** The visual mapper. Generates Mermaid.js state flows and defines WCAG-compliant, atomic UI components using utility-first CSS, driven by the `style_guide.md`.
5. **Engineering (`engineering.xml`):** The builder & janitor. Drafts ADRs for your approval, writes Interfaces/Mocks first, executes TDD (Red-Green-Harden), runs linters, integrates `shadcn/ui` components, and ruthlessly deletes dead code during Teardowns. 
6. **Growth/Ops (`growth_ops.xml`):** The privacy officer and analyst. Enforces compliance, defines infrastructure "Kill Switches" (e.g., alert thresholds), evaluates strict A/B or Pre/Post cohorts, and commands Teardowns.

## 👤 The Operator's Role (Human-in-the-Loop)

You are the CEO, the lead investor, and the final decision-maker. You **do not** write code or draft specs. Your job is to:
1. **Provide raw signals:** Feed user pain points into the prompt.
2. **Approve Architecture:** When the pipeline pauses with `ADR_STATE: [Pending Human]`, you read the drafted ADR in `docs/product/adr/` and change its status to "Accepted".
3. **Provide Raw Data:** When Growth/Ops asks for launch metrics, you paste the raw numbers from your dashboard (Datadog, PostHog, etc.).
4. **Curate the Memory:** Update `docs/company/lessons_learned.md` when an agent makes a mistake, ensuring it never happens twice.

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
skills/               # The LLM prompt definitions
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

## 🏗️ Infrastructure & Continuous Integration

This OS is built on a strict **"Git Push to Deploy"** PaaS (Platform-as-a-Service) model:
* **Zero Custom Cloud-Formation:** We explicitly ban complex orchestrators (Kubernetes, Terraform) to avoid maintenance debt. 
* **Backend:** Handled by a single highly optimized `Dockerfile` in `src/api/` intended for Render or Railway.
* **Frontend:** Deployed instantly via Vercel or Netlify directly from the `src/web/` directory.
* **Security & CI Gate:** All commits pushed to `main` trigger GitHub Actions. This pipeline runs Ruff (SAST), Biome, Pytest, Vitest, and TruffleHog (Verified Secret Scanning). **Only green builds are deployed.**

## 🎨 Design System & Headless Components

The OS utilizes **Code as the Design Kit**. There is no Figma. 
* **The Visual Style Guide:** Located at `docs/product/style_guide.md`, this dictates spacing, vibe, and semantic colors.
* **Shadcn/UI:** The Engineering agent generates accessible, un-styled Radix components on the fly (via `components.json`) directly into the `src/web/components/ui/` folder.
* **Tailwind CSS:** Components are styled using the strict semantic variables locked into `tailwind.config.js` and `index.css`.

## 🛠️ How To Use It

You interface with the entire company through a single command: `python orchestrator.py "Your prompt here"`.

### The Standard Workflow
When a user requests a new feature:
```bash
python orchestrator.py "3 users asked for data exports in the feedback log."
```
*The Orchestrator wakes up Strategy -> Spec -> Engineering (ADR Draft) -> [PAUSE FOR YOUR APPROVAL] -> Engineering (Build) -> Ops.*

### Fast-Track: The Hotfix
When a test fails, or you need to tweak UI, bypass Strategy and Spec:
```bash
python orchestrator.py "[HOTFIX] The button on the landing page is blue, make it red."
```

### Fast-Track: The Teardown
When an experiment fails, order the Engineering agent to aggressively scrub the codebase:
```bash
python orchestrator.py "[TEARDOWN] The A/B test lost. Delete the variant B webhook settings code and UI."
```

## ⚖️ Do's and Don'ts

* **DO use `lessons_learned.md`:** If an agent hallucinates a Tailwind class or uses an outdated library, add a bullet point here.
* **DO let the pre-commit hook work:** If `git commit` fails, do not bypass it. Use the `[HOTFIX]` command and force the AI to fix its own mess.
* **DON'T bypass the ADR process:** Never let agents arbitrarily decide to add Postgres or Redis without your explicit "Accepted" stamp.
* **DON'T let agents write to `architecture.md`:** Only the Engineering agent is allowed to update this file, and only *after* an ADR is accepted.
* **DON'T bloat the backlog:** Strategy will actively try to kill bad ideas. Let it.

## 💡 Helpful Tips

* **Smart Routing:** Keep `SMART_ROUTING=true` in your `.env`. The Orchestrator automatically routes logic-heavy tasks (Strategy) to deep-reasoning models, coding tasks to Claude 3.7 Sonnet, and formatting tasks to cheaper models.
* **Context Pruning:** The Orchestrator uses deterministic pruning (`tail_file`) to only send the most recent logs to the AI, saving you massive API costs.
* **Dependabot Auto-Merge:** Rely on your `ci.yml` safety net. Let Dependabot merge non-breaking dependency updates automatically in the background.