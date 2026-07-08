from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class LeadStatus(str, Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    lost = "lost"


class LeadSortField(str, Enum):
    id = "id"
    name = "name"
    email = "email"
    phone = "phone"
    company = "company"
    source = "source"
    status = "status"
    created_at = "created_at"
    updated_at = "updated_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class LeadCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, min_length=1, max_length=50)
    company: str | None = Field(default=None, min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=100)


class LeadUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=50)
    company: str | None = Field(default=None, min_length=1, max_length=100)
    source: str | None = Field(default=None, min_length=1, max_length=100)
    status: LeadStatus | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        return self


class LeadRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
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
