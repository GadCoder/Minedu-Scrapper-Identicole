from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class School(BaseModel):
    id: Optional[int] = Field(None, description="Primary key, auto-increment")
    id_codmod: str = Field(..., max_length=255, description="ID Codmod")
    cod_mod: str = Field(..., max_length=255, description="Cod Mod")
    cod_local: str = Field(..., max_length=255, description="Cod Local")
    name: str = Field(..., max_length=255, description="School Name")
    direction: str = Field(..., max_length=255, description="School Direction")
    type: str = Field(..., max_length=255, description="School Type")
    cost: int = Field(..., description="School Cost")
    cost_year: int = Field(..., description="School Yearly Cost")
    students_number: int = Field(..., description="Number of Students")
    level: str = Field(..., max_length=255, description="Education Level")
    shift: str = Field(..., max_length=255, description="School Shift")
    genre_type: int = Field(..., description="Genre Type")
    sex_type: int = Field(..., description="Sex Type")
    sex_type_text: str = Field(..., max_length=255, description="Sex Type Text")
    latitude: Decimal = Field(..., description="Latitude Coordinates", decimal_places=8)
    longitude: Decimal = Field(
        ..., description="Longitude Coordinates", decimal_places=8
    )
    ubigeo_code: str = Field(..., max_length=255, description="Ubigeo Code")
    modality_text: str = Field(..., max_length=255, description="Modality Text")
    modality_code: str = Field(..., max_length=20, description="Modality Code")
    stage_text: str = Field(..., max_length=255, description="Stage Text")
    stage_code: str = Field(..., max_length=20, description="Stage Code")
    region_code: str = Field(..., max_length=20, description="Foreign Key to Region")
    province_code: str = Field(
        ..., max_length=10, description="Foreign Key to Province"
    )
    district_code: str = Field(
        ..., max_length=10, description="Foreign Key to District"
    )

    class Config:
        orm_mode = True
