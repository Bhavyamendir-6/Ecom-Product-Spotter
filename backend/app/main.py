import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to sys.path so we can import existing sub_agents
_project_root = Path(__file__).resolve().parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from app.config import get_settings
from app.database import close_engine, create_tables
from app.exceptions import register_exception_handlers
from app.routers import analysis, history, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await close_engine()


settings = get_settings()

app = FastAPI(
    title="E-Commerce Product Spotter API",
    description="Discover trending product opportunities from Reddit data",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(analysis.router)
app.include_router(history.router)
app.include_router(ws.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
