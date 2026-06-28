from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    LeadCount,
    LeadCreate,
    LeadDeleteResponse,
    LeadRead,
    LeadStatus,
    LeadUpdate,
)

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
def get_leads(
        status: LeadStatus | None = None,
        source: str | None = None,
        search: str | None = Query(default=None, min_length=1, max_length=100),
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
        db: Session = Depends(get_db),
):
    status_value = status.value if status else None

    return crud.get_leads(
        db,
        status=status_value,
        source=source,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/count", response_model=LeadCount)
def count_leads(
        status: LeadStatus | None = None,
        source: str | None = None,
        search: str | None = Query(default=None, min_length=1, max_length=100),
        db: Session = Depends(get_db),
):
    status_value = status.value if status else None

    count = crud.count_leads(
        db,
        status=status_value,
        source=source,
        search=search,
    )

    return {"count": count}


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


@router.delete("/{lead_id}", response_model=LeadDeleteResponse)
def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead_by_id(db, lead_id)

    if not lead:
        raise HTTPException(
            status_code=404,
            detail=f"Lead with id {lead_id} doesn't exist",
        )

    crud.delete_lead(db, lead)

    return {"message": f"Lead with id {lead_id} deleted successfully"}
