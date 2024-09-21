import os
import json
import requests
import mysql.connector
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from models.location_data import LocationData
from insert_school_data import insert_school

load_dotenv()


def create_sql_connection():
    connection = mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=os.getenv("database"),
    )
    return connection


def get_departments_data(connection):
    cursor = connection.cursor()
    query = """
        SELECT region.name as 'region_name',
            region.code as 'region_code',
            p.name as 'province_name',
            p.province_code as 'province_code'
        FROM region
            INNER JOIN province p on region.code = p.region_code
        ;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results


def transform_location_data(locations: list) -> list[LocationData]:
    location_data = []
    for location in locations:
        location_data.append(
            LocationData(
                region_name=location[0],
                region_code=location[1],
                province_name=location[2],
                province_code=location[3],
            )
        )
    return location_data


def create_data_for_query(location: LocationData):
    data = {
        "accion": "Detalle",
        "ubicacion": "1",
        "s_departament_geo": location.region_code,
        "s_province_geo": location.province_code,
        "s_district_geo	": "",
        "txt_cen_edu": "",
        "modalidad": "01",
        "s_nivel": "B0",
        "vacante": "3",
        "participa": "3",
        "dot-amount": "5",
        "genero": "",
    }
    return data


def get_schools_data(location: LocationData, connection):
    data = create_data_for_query(location=location)
    location_name = f"{location.region_name}-{location.province_name}"
    index = 0
    page_has_data = True
    schools_number = 0
    while page_has_data:
        schools_data = get_schools_pagination_data(
            location=location, page=index, data=data, connection=connection
        )
        if schools_data == 0:
            page_has_data = False
            break
        schools_number += schools_data
        index += 12
    print(f"Se encontraron {schools_number} colegios para {location_name}")


def get_schools_pagination_data(
    location: LocationData, page: int, data: dict, connection
):
    url = f"https://identicole.minedu.gob.pe//colegio/busqueda_colegios_detalle/{page}"
    response = requests.post(url, data=data)
    location_name = f"{location.region_name}-{location.province_name}"
    status_code = response.status_code
    if status_code != 200:
        print(f"! Error al obtener colegios para {location_name} -> {status_code}")
        return
    parts = response.text.split("||")
    if len(parts) < 4:
        print(f"! No se encontraron colegios para {location_name} - page {page}")
        return 0
    schools = json.loads(parts[3])
    if not schools:
        return 0
    for school in schools:
        try:
            insert_school(connection=connection, json_data=school)
        except Exception as e:
            continue
    return len(schools)


def main():
    connection = create_sql_connection()
    locations = get_departments_data(connection=connection)
    location_data: list[LocationData] = transform_location_data(locations=locations)
    for location in location_data:
        get_schools_data(location=location, connection=connection)


if __name__ == "__main__":
    main()
