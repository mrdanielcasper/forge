# Lessons Learned (System Memory)

## Global Constraints
- **Idempotency:** When updating a markdown file (like `current_run.md` or `backlog.md`), overwrite the existing block for that specific feature. Do not endlessly append duplicate blocks.
- **Tone:** Do not use corporate jargon (e.g., "synergy", "paradigm shift"). Speak in direct, plain English.

## Design
- **Tailwind Height:** Never use `h-screen` for mobile layouts as it breaks on iOS Safari. Always use `min-h-screen` or `min-h-[100dvh]`.
- **Buttons:** Always use the Shadcn `Button` component. Never write `<button class="...">` from scratch.
- **Empty States:** Every table or list component must have an explicit empty state illustration or text block. 
- **Images & Placeholders:** Never hallucinate production image URLs. Use `lucide-react` for all icons. If a layout needs an image, use a deterministic placeholder (e.g., `https://placehold.co/600x400`) until the founder provides the real asset in the `public/` folder. Do not attempt to write raw, complex `<svg>` illustration code.

## Engineering
- **No Raw HTML Injection:** NEVER use React's `dangerouslySetInnerHTML` or inject raw, unparsed HTML strings into the DOM. This is a severe XSS security risk and bypasses our TypeScript/JSX safety nets. If rendering rich text or Markdown, use a sanitized parser (e.g., `react-markdown`) or map the data to native React components.
- **Microcopy:** Never hardcode user-facing strings (like button text, error messages, or empty states) directly into React components. Always import and use the `content` object from `src/web/lib/content.ts`. If the copy doesn't exist yet, add it to the dictionary first.
- **No Console Logging:** Never use `console.log()` to suppress or swallow errors in production. Pipe errors to the UI or use structured backend logging. 
- **Database Mocks:** Never write tests that require a live Postgres connection. Always use MSW (Mock Service Worker) for APIs and in-memory arrays for DB tests.
- **Date Handling:** Never use the native `Date()` object for timezone-sensitive calculations. Always use `date-fns`.
- **Environment Variables (Mocks):** Never name the test webhook URL anything other than `TEST_WEBHOOK_URL` in the `.env.mock` file. 
- **Environment Variables (Production):** Never use `os.environ.get()` for runtime application logic. Always define a Pydantic `BaseSettings` class. This ensures the Docker container fails to boot if a production secret is missing, protecting zero-downtime deployments.
- **Containerization:** When writing Dockerfiles for the FastAPI backend, always use a multi-stage build. Use `uv` to install dependencies in the builder stage to keep the final production image minimal. Never run the app as the `root` user.

## Strategy & Ops
- **Test Types:** Never recommend an A/B test unless the feature targets the public landing page. Deep-app features lack the traffic for statistical significance; always use Pre/Post Cohorts.
- **Marketing Copy:** Never use the word "Revolutionary" in any changelog or email blast.

## Tech Stack Constraints
- **Testing:** We use `pytest` and `pytest-bdd` for Python. We use `Vitest` for TypeScript. NEVER generate Jest, Mocha, or `unittest` files.
- **Linting:** We use `Ruff` and `Biome`. NEVER generate `.eslintrc`, `.prettierrc`, `tox.ini`, or `setup.cfg` files.
- **Frameworks:** Backend is FastAPI. Frontend is Vite + React. Do not generate Next.js `pages/` or `app/` routers.

## Accessibility (A11y)
- **No Overlays:** NEVER use third-party accessibility overlay widgets or SaaS tools. They introduce performance debt and legal risk. 
- **Automated Scanning:** All frontend accessibility testing must be done natively in CI using `@axe-core/playwright`.
- **Semantic HTML:** Always prefer native HTML elements (e.g., `<button>`, `<dialog>`) or `shadcn/ui` primitives over custom `div` implementations to ensure native screen-reader support.

## Version Control
- **Branching Strategy:** We use a strict Short-Lived Feature Branch model. Do not recommend GitFlow, Release branches, or Staging environments. Every branch branches from `main` and merges back to `main`.
- **Commit Messages:** All commits must follow the Conventional Commits specification (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`). Always append the Backlog ID from `current_run.md` to the end of the commit message (e.g., `[B-001]`).
- **Merging Strategy (Squash & Merge):** All Pull Requests MUST be merged using "Squash and Merge" to keep the `main` branch history clean. One feature branch equals exactly one commit on `main`. Always delete the feature branch immediately after merging.

## Security Baselines (OWASP Top 10 Prevention)
- **XSS & CSP:** We rely on React's native string escaping and strictly forbid `dangerouslySetInnerHTML`. Furthermore, the frontend hosting configuration MUST include a strict Content Security Policy (CSP) header that bans `unsafe-inline` and `unsafe-eval` scripts.
- **SQL Injection (SQLi):** NEVER construct raw SQL queries using string concatenation or f-strings. All database interactions MUST be parameterized or use the designated ORM/database client (e.g., Supabase SDK, SQLAlchemy).
- **Strict Input Validation:** NEVER use `typing.Any` or un-typed `dict` payloads in FastAPI Pydantic schemas. Every input must be explicitly typed, and string fields must have defined `max_length` constraints to prevent buffer/memory exhaustion attacks.
- **CSRF Protection:** If the API uses cookie-based authentication, the backend MUST implement standard CSRF token middleware. (If using standard Bearer tokens via Auth headers, this is not required).
- **Rate Limiting:** Any unauthenticated endpoint (e.g., Login, Webhook ingestion, Password Reset) MUST be wrapped in a rate-limiter to prevent brute-force attacks and DDoS.
- **Supply Chain & Package Updates:** We rely on GitHub Dependabot for all `npm`, `uv`, and GitHub Action updates. Dependabot PRs should be merged quickly, relying on our automated `pytest` and `playwright` suites to catch breaking changes.
- **Docker Immutability:** When writing Dockerfiles, NEVER use the `:latest` tag for base images. Always pin to a specific version (e.g., `python:3.11.4-slim`), and preferably pin to the exact SHA-256 digest to prevent upstream image poisoning.
- **Log Masking & PII:** Never log raw request bodies, API keys, passwords, or PII in structured logs. The backend MUST implement a sanitization utility that masks sensitive fields (e.g., replacing passwords with `***`) before passing data to the logger.

## Template Usage
- **Design Agent:** Always use `docs/templates/design_blueprint.md` when generating UI handoffs.
- **Ops Agent:** Always use `docs/templates/teardown_manifest.md` when ordering the deletion of a killed feature.