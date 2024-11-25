import os
import time
import json

import mysql.connector
import requests
from dotenv import load_dotenv

from models.location_data import LocationData

load_dotenv()


def create_sql_connection(database: str):
    connection = mysql.connector.connect(
        host=os.getenv("host"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        database=database,
    )
    return connection


def get_departments_data(connection, database: str):
    cursor = connection.cursor()
    query = f"""
        SELECT
            region.name, region.code,
            p.name, p.province_code,
            d.name as 'district_name',
            d.district_code as 'district_code'
        FROM region
        INNER JOIN {database}.province p on region.code = p.region_code;
        INNER JOIN {database}.district d on p.code = d.province_code;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results


def transform_location_data(locations: list) -> list[LocationData]:
    location_data = []
    for location in locations:
        location_data.append(LocationData(location=location))
    return location_data


def get_schools_from_location(location: LocationData, modality: str, stage: str):
    data = get_request_data(location=location, modality=modality, stage=stage)
    location_name = f"{location.region_name}-{location.province_name}"
    number_of_schools = get_number_of_schools(data=data, location_name=location_name)
    if number_of_schools == 0:
        return 0
    number_of_pages = get_number_of_pages(number_of_schools=number_of_schools)
    save_schools(number_of_pages=number_of_pages, data=data)
    return number_of_schools


def get_number_of_schools(data: dict, location_name: str):
    url = "https://identicole.minedu.gob.pe/colegio/busqueda_colegios_detalle"
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"\t! No se encontraron colegios para {location_name}")
        return 0
    parts = response.text.split("||")
    if len(parts) < 4:
        print(f"! No se encontraron colegios para {location_name}")
        return False
    number_of_schools = int(parts[2])
    return number_of_schools


def get_number_of_pages(number_of_schools: int):
    number_of_pages = number_of_schools // 12
    if number_of_schools % 12 != 0:
        number_of_pages += 1
    return number_of_pages


def get_request_data(location: LocationData, modality: str, stage: str):
    data = {
        "accion": "Detalle",
        "ubicacion": "1",
        "s_departament_geo": location.region_code,
        "s_province_geo": location.province_code,
        "s_district_geo": "01",
        "txt_cen_edu": "",
        "modalidad": modality,
        "s_nivel": stage,
        "vacante": "3",
        "participa": "3",
        "dot-amount": "5",
        "genero": "",
    }
    return data


def save_schools(number_of_pages: int, data: dict):
    url = f"https://identicole-scrapper-api.gadsw.dev/save-schools-from-location?number_of_pages={number_of_pages}"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    requests.post(url, json=data, headers=headers)


def main():
    database = "schools_data_workers"
    connection = create_sql_connection(database=database)
    locations = get_departments_data(connection=connection, database=database)
    location_data: list[LocationData] = transform_location_data(locations=locations)
    modalities = ["01", "03", "04"]
    stages = ["A1,A2,A3", "B0", "A5", "F0"]
    start_time = time.time()
    for location in location_data:
        schools_founded = 0
        location_name = f"{location.region_name}-{location.province_name}"
        print(f"Getting schools for {location_name}")
        for modality in modalities:
            for stage in stages:
                schools_founded += get_schools_from_location(
                    location=location,
                    modality=modality,
                    stage=stage,
                )
        print(f"\tFounded {schools_founded} schools for {location_name}")

    end_time = time.time()
    elapsed_time_seconds = end_time - start_time
    elapsed_time_minutes = elapsed_time_seconds / 60

    print(f"Elapsed time: {elapsed_time_minutes:.2f} minutes")


if __name__ == "__main__":
    main()
