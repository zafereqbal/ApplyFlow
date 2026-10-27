from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import Base, engine
from app import models  # noqa: F401
from app.routes import auth, applications, dashboard

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenient for local portfolio setup; use Alembic migrations as the deployment release step.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", description="Job application tracker API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["operations"])
def health():
    return {"status": "ok", "service": settings.app_name}
