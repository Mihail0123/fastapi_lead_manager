from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.schemas import LeadCreate, LeadRead, LeadUpdate
from app import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lead Manager API")


@app.get("/")
def root():
    return {"message": "Lead Manager API is running"}


@app.get("/health")
def health_check():
    return {"status": "OK"}


@app.post("/leads", response_model=LeadRead)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    email = str(lead_data.email)

    existing_lead = crud.get_lead_by_email(db, email)

    if existing_lead:
        raise HTTPException(
            status_code=400,
            detail=f"Lead with email {lead_data.email} already exists",
        )

    return crud.create_lead(db, lead_data)


@app.get("/leads", response_model=list[LeadRead])
def get_leads(db: Session = Depends(get_db)):
    return crud.get_leads(db)


@app.get("/leads/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist"
        )

    return lead


@app.patch("/leads/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist",
        )

    return crud.update_lead_status(db, lead, lead_data)


@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist"
        )

    crud.delete_lead(db, lead)

    return {"message": f"Lead with id {lead_id} deleted successfully"}
