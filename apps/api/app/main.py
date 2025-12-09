from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.security import get_current_user
from app.core.config import settings
from app.routers import auth, decks, note_types, notes, study

app = FastAPI(title="Nihon Flash API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(decks.router, dependencies=[Depends(get_current_user)])
app.include_router(note_types.router, dependencies=[Depends(get_current_user)])
app.include_router(notes.router, dependencies=[Depends(get_current_user)])
app.include_router(study.router, dependencies=[Depends(get_current_user)])
