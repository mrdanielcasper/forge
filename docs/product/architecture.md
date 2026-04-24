# Product Architecture

## Principles
- Keep the system narrow, testable, and easy to change.
- Separate domain logic from transport, storage, and UI details.
- Favor mocked-first delivery for new workflows until demand is proven.

## Core Boundaries
- Product decisions live in briefs and contracts, not only in code comments.
- UI concerns should be separated from workflow and integration logic.
- External services such as Discord should be wrapped behind explicit interfaces.

## Non-Negotiables
- Sensitive values must not be logged in plaintext.
- Error states must be explicit in both the product contract and implementation.
- Active delivery work must be tracked in docs/product/current_run.md.

## ADR Trigger
Create an ADR when a change affects system boundaries, external integrations, or long-term maintenance cost.

## Tooling & Execution Stack
- **Backend Framework:** Python / FastAPI
- **Frontend Framework:** TypeScript / Vite / React / Tailwind
- **Python Linting & Testing:** `uv` for packages, `ruff` for lint/format, `pytest` + `pytest-bdd` for testing.
- **JS/TS Linting & Testing:** `npm` for packages, `Biome` for lint/format, `Vitest` for unit tests, `Playwright` + `@axe-core/playwright` for E2E and A11y scanning.
- *Constraint:* The Engineering agent MUST use these tools. Do not install or configure ESLint, Prettier, Jest, Black, Flake8, Django, or Webpack.

## Accessibility (A11y)
- **Native Compliance:** Accessibility is a strict architectural baseline. We rely on `shadcn/ui` for accessible DOM primitives (focus management, ARIA tags, keyboard navigation).
- **No Overlays:** NEVER introduce third-party accessibility overlay scripts or widgets (e.g., accessiBe, UserWay). They introduce performance debt and legal liability. 
- **CI Enforcement:** Automated WCAG scanning must be run natively in the testing pipeline using `@axe-core/playwright`.

## Codebase Structure
- **Backend Sandbox:** All Python API code MUST be placed in `src/api/`.
- **Frontend Sandbox:** All React/TS UI code MUST be placed in `src/web/`.

## Content & Microcopy
- **The Dictionary:** All user-facing strings (button labels, validation errors, empty states, descriptions) MUST be centralized in the Content Dictionary at `src/web/lib/content.ts`.
- **Zero Hardcoding:** Never hardcode text directly into React components. Components must import and reference the `content` object. This separates presentation from messaging.

## Design System & Theming
- **Headless Components:** We use `shadcn/ui` for accessible component primitives. The CLI writes code to `src/web/components/ui/` based on `components.json`. Do not write primitives from scratch.
- **Visual Brand:** Semantic colors, spacing, and border radii are locked in `docs/product/style_guide.md` and enforced via `tailwind.config.js` and `index.css`.

## Asset & Media Storage
- **Static Assets (Brand & UI):** Logos, favicons, and static UI illustrations (SVGs) belong in the `public/` directory at the root and MUST be committed to Git.
- **Dynamic Assets (User Uploads):** Avatars, document attachments, and user-generated media MUST be stored in an external Object Storage service (e.g., Supabase Storage, AWS S3). NEVER write user uploads to the local container filesystem.
- **Icons:** We strictly use `lucide-react` for all interface icons.

## Infrastructure & Hosting Boundaries
- **Sourcing Posture:** We strictly use Platform-as-a-Service (PaaS). Do NOT generate Terraform, AWS CloudFormation, or Kubernetes manifests.
- **Frontend Hosting:** Vercel (Deployed via Git integration).
- **Backend Hosting:** Render or Railway (Deployed via a single `Dockerfile`).
- **Database:** Serverless Postgres (e.g., Supabase) accessed via standard connection strings.
- **Constraint:** The Engineering agent is permitted to write `Dockerfiles` and PaaS config files (e.g., `render.yaml`), but it must NEVER hardcode production secrets.
- **Zero-Downtime Deployments:** The FastAPI backend MUST expose a lightweight `/health` endpoint. The PaaS uses this to verify Docker container readiness before routing live traffic.