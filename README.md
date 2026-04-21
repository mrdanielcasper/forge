# Solo Software Company OS

This repository is a lightweight, fully autonomous operating system for building and scaling a one-person software company. It replaces ad-hoc chat interfaces with a strict, deterministic agent pipeline designed to protect a solo founder's most precious resources: **Time, Focus, IP, and Capital.**

By tying Strategy, Product Definition, Design, Engineering, and Launch Operations to durable markdown artifacts, this OS prevents architectural bloat, ensures legal/compliance safety, and maintains a "Zero-Debt" codebase.

## 🚀 First Time Setup

1. **Environment Variables:** Copy `.env.example` to `.env` and add your API keys.
2. **Backend Dependencies:** We use `uv` for lightning-fast, deterministic package management.
   ```bash
   # Install uv if you don't have it
   curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
   
   # Initialize the project and lock dependencies
   uv init
   # Sync the locked dependencies (creates .venv automatically)
   uv sync
   ```
3. **Frontend Dependencies (JS/TS):** We use npm to lock in our strict linting and testing tools.
  ```bash
  # Install Biome, Vitest, and Playwright
  npm install
  ```
4. **Activate the Pre-Commit Bouncer:** This native Git hook prevents the AI from leaking secrets or faking test results.
   ```bash
   git config core.hooksPath scripts/githooks
   ```
  
### Note for you (The Operator):
When you run `uv init` and `uv add openai anthropic python-dotenv` on your machine for the first time, `uv` will create a `pyproject.toml` file and a `uv.lock` file. **You should commit both of those files to Git.** Once those files are in your repository, any future developer (or you, on a new laptop) will just run `uv sync` to perfectly replicate the environment.

## 🧠 The 6-Node Architecture

The OS is driven by a deterministic Python script (`orchestrator.py`) that acts as your Chief of Staff, routing tasks to 5 specialized LLM agents defined in the `skills/` folder.

1. **The Orchestrator (`orchestrator.py`):** A deterministic Python router. It parses routing tags, aggressively prunes context to save tokens, manages the multi-agent execution queue, and dynamically routes tasks to the most cost-effective LLM provider (`SMART_ROUTING`).
2. **Strategy (`strategy.xml`):** The business filter. Evaluates ideas based on Cost of Delay, Reversibility (1-Way vs 2-Way doors), Legal/Compliance risk, and Strategic Sourcing (Build vs. Buy vs. OSS). 
3. **Product Spec (`product_spec.xml`):** The architect's radar. Turns strategy into strict Feature Briefs and Data Contracts. Identifies when an idea crosses a system boundary and triggers an Architectural Decision Record (ADR).
4. **Design (`design.xml`):** The visual mapper. Generates Mermaid.js state flows and defines WCAG-compliant, atomic UI components using utility-first CSS.
5. **Engineering (`engineering.xml`):** The builder & janitor. Drafts ADRs for your approval, writes Interfaces/Mocks first, executes TDD (Red-Green-Harden), runs linters, and ruthlessly deletes dead code during Teardowns. 
6. **Growth/Ops (`growth_ops.xml`):** The privacy officer and analyst. Enforces compliance, defines infrastructure "Kill Switches" (e.g., alert thresholds), evaluates strict A/B or Pre/Post cohorts, and commands Teardowns.

## 👤 The Operator's Role (Human-in-the-Loop)

You are the CEO, the lead investor, and the final decision-maker. You **do not** write code or draft specs. Your job is to:
1. **Provide raw signals:** Feed user pain points into the prompt.
2. **Approve Architecture:** When the pipeline pauses with `ADR_STATE: [Pending Human]`, you read the drafted ADR in `docs/product/adr/` and change its status to "Accepted".
3. **Provide Raw Data:** When Growth/Ops asks for launch metrics, you paste the raw numbers from your dashboard (Datadog, PostHog, etc.).
4. **Curate the Memory:** Update `docs/company/lessons_learned.md` when an agent makes a mistake, ensuring it never happens twice.

## 📁 Repository Structure & Canonical Documents

```text
docs/
  company/
    thesis.md           # The business mission and strategic wedge
    scorecard.md        # The metrics that justify building
    feedback_log.md     # Raw evidence from users
    lessons_learned.md  # The global system memory (AI constraints)
  product/
    backlog.md          # Prioritized opportunities (Pain + Sourcing)
    current_run.md      # The single active delivery record
    architecture.md     # LIVE architecture (Updated ONLY by Engineering)
    flows.md            # Mermaid UI state diagrams
    adr/                # Architectural Decision Records
    briefs/             # Live feature specs
    contracts/          # Live API/Data schemas
  ops/
    launch_checklist.md # Launch readiness & infra Kill Switches
    experiment_log.md   # Outcome tracking
skills/                 # The LLM prompt definitions
scripts/
  githooks/
    pre-commit          # The zero-dependency security/testing bouncer
orchestrator.py         # The deterministic execution engine
```

## 🛠️ How To Use It

You interface with the entire company through a single command: `python orchestrator.py "Your prompt here"`.

### The Standard Workflow
When a user requests a new feature (e.g., "I wish I could export my data"):
```bash
python orchestrator.py "3 users asked for data exports in the feedback log."
```
*The Orchestrator wakes up Strategy -> Spec -> Engineering (ADR Draft) -> [PAUSE FOR YOUR APPROVAL] -> Engineering (Build) -> Ops.*

### Fast-Track: The Hotfix
When a test fails, or you need to fix a typo, bypass Strategy and Spec and go straight to code:
```bash
python orchestrator.py "[HOTFIX] The button on the landing page is blue, make it red."
```

### Fast-Track: The Teardown
When an experiment fails, order the Engineering agent to aggressively scrub the codebase of the dead feature:
```bash
python orchestrator.py "[TEARDOWN] The A/B test lost. Delete the variant B webhook settings code and UI."
```

## ⚖️ Do's and Don'ts

* **DO use `lessons_learned.md`:** If an agent hallucinates a Tailwind class or uses an outdated library, add a bullet point here. The Orchestrator injects this into every prompt.
* **DO let the pre-commit hook work:** If `git commit` fails because the AI broke a test, copy the error, use the `[HOTFIX]` command, and force the Engineering agent to fix its own mess.
* **DON'T bypass the ADR process:** Never let agents arbitrarily decide to add Postgres or Redis. Let them draft the ADR, but *you* must approve it.
* **DON'T let agents write to `architecture.md`:** Only the Engineering agent is allowed to update this file, and only *after* an ADR is accepted.
* **DON'T bloat the backlog:** Strategy will actively try to kill bad ideas. Let it.

## 💡 Helpful Tips

* **Smart Routing:** Keep `SMART_ROUTING=true` in your `.env`. The Orchestrator will automatically route logic-heavy tasks (Strategy) to deep-reasoning models (o3-mini), coding tasks to Claude 3.7 Sonnet, and formatting tasks to cheap models (GPT-4o-mini).
* **Context Pruning:** Don't worry about your feedback logs getting too long. The Orchestrator uses deterministic pruning (`tail_file`) to only send the most recent signals to the AI, saving you massive API costs.
* **Reversibility is Key:** The Strategy agent grades ideas as "1-Way Doors" or "2-Way Doors". Trust this system. Move incredibly fast on 2-Way Doors (UI tweaks), but pause and demand heavy validation on 1-Way Doors (Schema changes, pricing shifts).