from fastapi import FastAPI

from app.database import Base, engine
from app.models.lead import Lead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Manager API")


@app.get("/")
def root():
    return {"message": "Lead Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "OK"}
