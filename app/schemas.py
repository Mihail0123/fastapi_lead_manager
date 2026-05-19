from pydantic import BaseModel, EmailStr


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    source: str


class LeadRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    source: str
    status: str

    model_config = {
        "from_attributes": True
    }