from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas import LeadCreate, LeadUpdate


def _apply_lead_filters(
        query,
        status: str | None = None,
        source: str | None = None,
        company: str | None = None,
        search: str | None = None,
):
    if status:
        query = query.filter(Lead.status == status)

    if source:
        query = query.filter(Lead.source == source)

    if company:
        query = query.filter(Lead.company == company)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Lead.name.ilike(search_pattern)) |
            (Lead.email.ilike(search_pattern)) |
            (Lead.phone.ilike(search_pattern)) |
            (Lead.company.ilike(search_pattern))
        )

    return query


def get_leads(
        db: Session,
        status: str | None = None,
        source: str | None = None,
        company: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 10,
):
    query = db.query(Lead)

    query = _apply_lead_filters(
        query,
        status=status,
        source=source,
        company=company,
        search=search,
    )

    return query.order_by(Lead.id).offset(skip).limit(limit).all()


def count_leads(
        db: Session,
        status: str | None = None,
        source: str | None = None,
        company: str | None = None,
        search: str | None = None,
):
    query = db.query(Lead)

    query = _apply_lead_filters(
        query,
        status=status,
        source=source,
        company=company,
        search=search,
    )

    return query.count()


def get_lead_status_stats(db: Session):
    rows = (
        db.query(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .all()
    )

    stats = {
        "new": 0,
        "contacted": 0,
        "qualified": 0,
        "lost": 0,
    }

    for status, count in rows:
        stats[status] = count

    return stats


def get_lead_source_stats(db: Session):
    rows = (
        db.query(Lead.source, func.count(Lead.id))
        .group_by(Lead.source)
        .all()
    )

    return {
        source: count
        for source, count in rows
    }


def get_lead_by_id(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()


def get_lead_by_email(db: Session, email: str):
    return db.query(Lead).filter(Lead.email == email).first()


def create_lead(db: Session, lead_data: LeadCreate):
    lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
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
