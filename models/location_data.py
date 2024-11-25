

class LocationData():
    def __init__(self, location: list) -> None:
        pass
        self.region_name: str = location[0]
        self.region_code: str = location[1]
        self.province_name: str = location[2]
        self.province_code: str = location[3]
        self.district_name: str = location[4]
        self.district_code: str = location[5]
