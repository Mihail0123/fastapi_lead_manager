from fastapi import FastAPI

from app.database import Base, engine
from app.routers import leads

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Manager API")

app.include_router(leads.router)


@app.get("/")
def root():
    return {"message": "Lead Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "OK"}
