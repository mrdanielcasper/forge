from fastapi import FastAPI

app = FastAPI(title="Solopreneur OS API")


@app.get("/health")
def health_check():
    """Zero-downtime deployment health check."""
    return {"status": "ok", "message": "API is online"}
