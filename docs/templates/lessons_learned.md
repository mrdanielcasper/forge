# Lessons Learned (System Memory)

## Global Constraints
- **Idempotency:** When updating a markdown file (like `current_run.md` or `backlog.md`), overwrite the existing block for that specific feature. Do not endlessly append duplicate blocks.
- **Tone:** Do not use corporate jargon (e.g., "synergy", "paradigm shift"). Speak in direct, plain English.

## Design
- **Tailwind Height:** Never use `h-screen` for mobile layouts as it breaks on iOS Safari. Always use `min-h-screen` or `min-h-[100dvh]`.
- **Buttons:** Always use the Shadcn `Button` component. Never write `<button class="...">` from scratch.
- **Empty States:** Every table or list component must have an explicit empty state illustration or text block. 

## Engineering
- **Database Mocks:** Never write tests that require a live Postgres connection. Always use MSW (Mock Service Worker) for APIs and in-memory arrays for DB tests.
- **Date Handling:** Never use the native `Date()` object for timezone-sensitive calculations. Always use `date-fns`.
- **Environment Variables:** Never name the test webhook URL anything other than `TEST_WEBHOOK_URL` in the `.env.mock` file.

## Strategy & Ops
- **Test Types:** Never recommend an A/B test unless the feature targets the public landing page. Deep-app features lack the traffic for statistical significance; always use Pre/Post Cohorts.
- **Marketing Copy:** Never use the word "Revolutionary" in any changelog or email blast.

## Engineering Constraints
- **Testing:** We use `pytest` and `pytest-bdd` for Python. We use `Vitest` for TypeScript. NEVER generate Jest, Mocha, or `unittest` files.
- **Linting:** We use `Ruff` and `Biome`. NEVER generate `.eslintrc`, `.prettierrc`, `tox.ini`, or `setup.cfg` files.
- **Frameworks:** Backend is FastAPI. Frontend is Vite + React. Do not generate Next.js `pages/` or `app/` routers.