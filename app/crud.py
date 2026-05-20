from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas import LeadCreate, LeadUpdate


def get_leads(db: Session):
    return db.query(Lead).order_by(Lead.id).all()


def get_lead_by_id(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_lead_by_email(db: Session, email: str):
    return db.query(Lead).filter(Lead.email == email).first()


def create_lead(db: Session, lead_data: LeadCreate):
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        source=lead_data.source,
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


def update_lead_status(db: Session, lead: Lead, lead_data: LeadUpdate):
    lead.status = lead_data.status.value

    db.commit()
    db.refresh(lead)

    return lead


def delete_lead(db: Session, lead: Lead):
    db.delete(lead)
    db.commit()