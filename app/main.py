from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.lead import Lead
from app.schemas import LeadCreate, LeadRead

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
    existing_lead = db.query(Lead).filter(Lead.email == lead_data.email).first()

    if existing_lead:
        raise HTTPException(
            status_code=400,
            detail=f"Lead with email {lead_data.email} already exists"
        )

    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        source=lead_data.source,
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


@app.get("/leads", response_model=list[LeadRead])
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.id).all()
    return leads