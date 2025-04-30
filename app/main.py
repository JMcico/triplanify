from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="Triplanify API")

app.include_router(routes.router, prefix="/api")