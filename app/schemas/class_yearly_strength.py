from pydantic import BaseModel, field_validator
from typing import Optional


class ClassYearlyStrengthCreate(BaseModel):
    class_id: int
    academic_year: str
    strength: int

    @field_validator("academic_year")
    def validate_year(cls, value):
        if len(value) != 9 or value[4] != "-":
            raise ValueError("Academic year must be in format YYYY-YYYY e.g. 2025-2026")
        parts = value.split("-")
        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            raise ValueError("Academic year must contain valid years")
        if end != start + 1:
            raise ValueError("End year must be exactly one year after start year")
        return value

    @field_validator("strength")
    def validate_strength(cls, value):
        if value < 1:
            raise ValueError("Class strength must be at least 1")
        if value > 200:
            raise ValueError("Class strength seems unrealistically high")
        return value


class ClassYearlyStrengthResponse(BaseModel):
    class_id: int
    academic_year: str
    strength: int
    class_name: Optional[str] = None

    class Config:
        from_attributes = True
