from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas import LeadCreate, LeadUpdate


def get_leads(
    db: Session,
    status: str | None = None,
    source: str | None = None,
    search:str | None = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Lead)

    if status:
        query = query.filter(Lead.status == status)

    if source:
        query = query.filter(Lead.source == source)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_pattern)) |
            (Lead.email.ilike(search_pattern))
        )

    return query.order_by(Lead.id).offset(skip).limit(limit).all()


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