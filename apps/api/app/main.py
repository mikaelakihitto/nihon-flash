from fastapi import FastAPI

from app.routers import auth, decks

app = FastAPI(title="Nihon Flash API")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(decks.router)
