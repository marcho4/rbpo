from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.db.models import LeadStatus

MAX_USERNAME_LENGTH = 50
MIN_USERNAME_LENGTH = 6
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 100
MAX_EMAIL_LENGTH = 255
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 255
MIN_SECTOR_LENGTH = 1
MAX_SECTOR_LENGTH = 255
MIN_TITLE_LENGTH = 1
MAX_TITLE_LENGTH = 255


class UserBase(BaseModel):
    username: str = Field(..., min_length=MIN_USERNAME_LENGTH, max_length=MAX_USERNAME_LENGTH)
    email: EmailStr


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyBase(BaseModel):
    name: str = Field(..., min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    sector: str = Field(..., min_length=MIN_SECTOR_LENGTH, max_length=MAX_SECTOR_LENGTH)


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=MIN_NAME_LENGTH, max_length=MAX_NAME_LENGTH)
    sector: Optional[str] = Field(None, min_length=MIN_SECTOR_LENGTH, max_length=MAX_SECTOR_LENGTH)


class CompanyResponse(CompanyBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    title: str = Field(..., min_length=MIN_TITLE_LENGTH, max_length=MAX_TITLE_LENGTH)
    description: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW


class LeadCreate(LeadBase):
    company_id: int


class LeadUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=MIN_TITLE_LENGTH, max_length=MAX_TITLE_LENGTH)
    description: Optional[str] = None
    status: Optional[LeadStatus] = None
    company_id: Optional[int] = None


class LeadResponse(LeadBase):
    id: int
    company_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    company: Optional[CompanyResponse] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
