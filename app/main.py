from fastapi import FastAPI

from app.routers import leads

app = FastAPI(title="Lead Manager API")

app.include_router(leads.router)


@app.get("/")
def root():
    return {"message": "Lead Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "OK"}
