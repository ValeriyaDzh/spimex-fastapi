from fastapi import FastAPI

from src.api.routers import spimex_router

app = FastAPI(title="Spimex")

app.include_router(spimex_router)
