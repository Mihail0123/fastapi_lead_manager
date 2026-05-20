from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import LeadCreate, LeadRead, LeadUpdate, LeadStatus

router = APIRouter(
    prefix="/leads",
    tags=["leads"],
)


@router.post("", response_model=LeadRead, status_code=201)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    email = str(lead_data.email)

    existing_lead = crud.get_lead_by_email(db, email)

    if existing_lead:
        raise HTTPException(
            status_code=400,
            detail=f"Lead with email {email} already exists",
        )

    return crud.create_lead(db, lead_data)


@router.get("", response_model=list[LeadRead])
def get_leads(status: LeadStatus | None = None, db: Session = Depends(get_db)):
    status_value = status.value if status else None
    return crud.get_leads(db, status=status_value)


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist",
        )

    return lead


@router.patch("/{lead_id}", response_model=LeadRead)
def update_lead(lead_id: int, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist",
        )

    return crud.update_lead_status(db, lead, lead_data)


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist",
        )

    crud.delete_lead(db, lead)

    return {"message": f"Lead with id {lead_id} deleted successfully"}
