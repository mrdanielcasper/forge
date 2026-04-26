from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/system", tags=["System"])


class SystemStatus(BaseModel):
    status: str
    version: str


@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Returns the current health status of the API."""
    return SystemStatus(status="operational", version="1.0.0")
