from pydantic import BaseModel, field_validator


class AcademicYearSettingCreate(BaseModel):
    academic_year: str
    total_working_days: int

    @field_validator("academic_year")
    def validate_year(cls, value):
        # check format is YYYY-YYYY
        if len(value) != 9 or value[4] != "-":
            raise ValueError("Academic year must be in format YYYY-YYYY e.g. 2025-2026")

        parts = value.split("-")
        if len(parts) != 2:
            raise ValueError("Academic year must be in format YYYY-YYYY e.g. 2025-2026")

        try:
            start = int(parts[0])
            end = int(parts[1])
        except ValueError:
            raise ValueError("Academic year must contain valid years e.g. 2025-2026")

        if end != start + 1:
            raise ValueError("End year must be exactly one year after start year")

        if start < 2000 or start > 2100:
            raise ValueError("Year must be between 2000 and 2100")

        return value

    @field_validator("total_working_days")
    def validate_days(cls, value):
        if value < 1 or value > 365:
            raise ValueError("Total working days must be between 1 and 365")
        return value

class AcademicYearSettingUpdate(BaseModel):
    total_working_days: int

    @field_validator("total_working_days")
    def validate_days(cls, value):
        if value < 1 or value > 365:
            raise ValueError("Total working days must be between 1 and 365")
        return value