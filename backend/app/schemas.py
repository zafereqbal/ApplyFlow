from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, model_validator

Status = Literal["saved", "applied", "screening", "interview", "offer", "rejected", "withdrawn"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ApplicationBase(BaseModel):
    company: str = Field(min_length=1, max_length=160)
    role: str = Field(min_length=1, max_length=160)
    job_url: HttpUrl | None = None
    status: Status = "saved"
    location: str | None = Field(default=None, max_length=160)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=10000)

    @model_validator(mode="after")
    def validate_salary_range(self):
        if self.salary_min is not None and self.salary_max is not None and self.salary_max < self.salary_min:
            raise ValueError("salary_max must be greater than or equal to salary_min")
        return self


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=160)
    role: str | None = Field(default=None, min_length=1, max_length=160)
    job_url: HttpUrl | None = None
    status: Status | None = None
    location: str | None = Field(default=None, max_length=160)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=10000)


class ApplicationOut(BaseModel):
    id: int
    company: str
    role: str
    job_url: str | None
    status: str
    location: str | None
    salary_min: int | None
    salary_max: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ApplicationPage(BaseModel):
    items: list[ApplicationOut]
    total: int
    page: int
    page_size: int


class DashboardSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    interview_rate_percent: float
    offer_count: int
