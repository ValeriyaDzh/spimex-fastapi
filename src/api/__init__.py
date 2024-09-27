__all__ = [
    "router",
]

from fastapi import APIRouter
from src.api.v1.routers import spimex_router_v1

router = APIRouter()
router.include_router(spimex_router_v1, prefix="/v1", tags=["Spimex | v1"])
