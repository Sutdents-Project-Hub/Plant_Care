from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import ai, announcements, auth, plants

app = FastAPI(title="Plant Care Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(plants.router, prefix="/api/v1/plant", tags=["plant"])
app.include_router(announcements.router, prefix="/api/v1/homepage", tags=["homepage"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])
