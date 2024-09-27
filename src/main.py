from fastapi import FastAPI

from src.api import router

app = FastAPI(title="Spimex")

app.include_router(router, prefix="/api")
