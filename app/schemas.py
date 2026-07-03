from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    lost = "lost"


class LeadCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    company: str | None = Field(default=None, min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=100)


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


class LeadStatusStats(BaseModel):
    new: int
    contacted: int
    qualified: int
    lost: int
