from fastapi import FastAPI
from api import routes

app = FastAPI(title="Triplanify API")

app.include_router(routes.router, prefix="/api")