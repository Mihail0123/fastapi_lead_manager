from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    lost = "lost"


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    source: str


class LeadUpdate(BaseModel):
    status: LeadStatus


class LeadRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: str | None
    source: str
    status: LeadStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class LeadCount(BaseModel):
    count: int


class LeadDeleteResponse(BaseModel):
    message: str
