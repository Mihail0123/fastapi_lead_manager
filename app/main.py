from fastapi import FastAPI

app = FastAPI(title="Lead Manager API")


@app.get("/")
def root():
    return {"message": "Lead Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "OK"}