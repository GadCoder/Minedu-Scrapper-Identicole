from pydantic import BaseModel


class LocationData(BaseModel):
    region_name: str
    region_code: str
    province_name: str
    province_code: str
    district_name: str
    district_code: str
