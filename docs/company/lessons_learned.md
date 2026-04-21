## Engineering Constraints
- **Testing:** We use `pytest` and `pytest-bdd` for Python. We use `Vitest` for TypeScript. NEVER generate Jest, Mocha, or `unittest` files.
- **Linting:** We use `Ruff` and `Biome`. NEVER generate `.eslintrc`, `.prettierrc`, `tox.ini`, or `setup.cfg` files.
- **Frameworks:** Backend is FastAPI. Frontend is Vite + React. Do not generate Next.js `pages/` or `app/` routers.
