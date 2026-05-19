from typing import Literal

from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    source: str


class LeadUpdate(BaseModel):
    status: Literal["new", "contacted", "qualified", "lost"]


class LeadRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    source: str
    status: str

    model_config = {
        "from_attributes": True
    }