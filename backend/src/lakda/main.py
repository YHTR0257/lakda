import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lakda.api import ask, documents, feedback, index

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

app = FastAPI(
    title="lakda Backend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router)
app.include_router(documents.router)
app.include_router(feedback.router)
app.include_router(index.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the lakda Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
