from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime, date

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    designation: str
    years_of_service: Optional[int] = None
    employment_number: int
    CNIC: str
    qualification: Optional[str] = None
    additional_responsibilities: Optional[str] = None
    extra_credentials: Optional[str] = None
    # teaching_load: Optional[int] = None
    joining_date: Optional[date] = None

    @field_validator("CNIC")
    def validate_cnic(cls, value):
        if not value.isdigit() or len(value) != 13:
            raise ValueError("CNIC must be exactly 13 digits")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain at least one symbol")
        return value

    @field_validator("first_name")
    def validate_first_name(cls, value):
        if not value.strip():
            raise ValueError("First name cannot be empty")
        return value.strip().title()

    @field_validator("last_name")
    def validate_last_name(cls, value):
        if not value.strip():
            raise ValueError("Last name cannot be empty")
        return value.strip().title()

    @field_validator("designation")
    def validate_designation(cls, value):
        allowed = ["teacher", "principal", "admin"]
        if value.lower() not in allowed:
            raise ValueError(f"Designation must be one of: {allowed}")
        return value.lower()
        
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    designation: Optional[str] = None
    years_of_service: Optional[int] = None
    employment_number: Optional[str] = None
    CNIC: Optional[str] = None
    qualification: Optional[str] = None
    additional_responsibilities: Optional[str] = None
    extra_credentials: Optional[str] = None

    @field_validator("CNIC")
    def validate_cnic(cls, value):
        if value is None:
            return value
        if not value.isdigit() or len(value) != 13:
            raise ValueError("CNIC must be exactly 13 digits")
        return value

    @field_validator("first_name")
    def validate_first_name(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("First name cannot be empty")
        return value.strip().title()

    @field_validator("last_name")
    def validate_last_name(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Last name cannot be empty")
        return value.strip().title()

    @field_validator("designation")
    def validate_designation(cls, value):
        if value is None:
            return value
        allowed = ["teacher", "chief coordinator", "peer coordinator", "principal", "admin"]
        if value.lower() not in allowed:
            raise ValueError(f"Designation must be one of: {allowed}")
        return value.lower()

class UserPublicResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    designation: str

    class Config:
        from_attributes = True


class UserFullResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    designation: str
    is_active: bool
    employment_number: int
    CNIC: str
    qualification: Optional[str] = None
    teaching_load: Optional[int] = None
    years_of_service: Optional[int] = None
    joined_at: Optional[datetime] = None
    must_change_password: bool

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    def validate_new_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        if not any(not char.isalnum() for char in value):
            raise ValueError("Password must contain at least one symbol")
        return value
    

    @field_validator("confirm_password")
    def passwords_match(cls, value, values):
        if "new_password" in values.data and value != values.data["new_password"]:
            raise ValueError("Passwords do not match")
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequestCreate(BaseModel):
    email: EmailStr
    reason: Optional[str] = None

class PasswordResetRequestResponse(BaseModel):
    request_id: int
    email: str
    reason: Optional[str] = None
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
