from fastapi import FastAPI

from src.api.routers.system import router as system_router

app = FastAPI(title="Solopreneur OS API")

app.include_router(system_router)


@app.get("/health")
def health_check():
    """Zero-downtime deployment health check."""
    return {"status": "ok", "message": "API is online"}
