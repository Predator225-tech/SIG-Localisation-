from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.db import open_pool, close_pool
from app.routers import ressources, sites, regions, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    open_pool()
    yield
    close_pool()

app = FastAPI(title="SIG Madagascar", description="Ressources naturelles de Madagascar", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.include_router(ressources.router, prefix="/api")
app.include_router(sites.router, prefix="/api")
app.include_router(regions.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
