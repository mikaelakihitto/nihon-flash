from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, decks, note_types, notes, study

app = FastAPI(title="Nihon Flash API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(decks.router)
app.include_router(note_types.router)
app.include_router(notes.router)
app.include_router(study.router)
