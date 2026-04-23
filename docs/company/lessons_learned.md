## Engineering Constraints
- **Testing:** We use `pytest` and `pytest-bdd` for Python. We use `Vitest` for TypeScript. NEVER generate Jest, Mocha, or `unittest` files.
- **Linting:** We use `Ruff` and `Biome`. NEVER generate `.eslintrc`, `.prettierrc`, `tox.ini`, or `setup.cfg` files.
- **Frameworks:** Backend is FastAPI. Frontend is Vite + React. Do not generate Next.js `pages/` or `app/` routers.
- **Containerization:** When writing Dockerfiles for the FastAPI backend, always use a multi-stage build. Use `uv` to install dependencies in the builder stage to keep the final production image minimal. Never run the app as the `root` user.
- **Environment Variables:** Never use os.environ.get() for runtime application logic. Always define a Pydantic BaseSettings class. This ensures the Docker container fails to boot if a production secret is missing, protecting zero-downtime deployments."