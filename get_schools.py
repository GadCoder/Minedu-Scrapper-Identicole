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
        host=os.getenv("host"),  # e.g., "localhost"
        user=os.getenv("user"),  # e.g., "root"
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
            p.province_code as 'province_code',
            d.name as 'district_name',
            d.district_code as 'district_code'
        FROM region
            INNER JOIN province p on region.code = p.region_code
            INNER JOIN district d on p.code = d.province_code
        ;
    """
    cursor.execute(query)
    # Step 4: Fetch and print the results (if using SELECT query)
    results = cursor.fetchall()
    # Step 5: Close the cursor and the connection
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
                district_name=location[4],
                district_code=location[5],
            )
        )
    return location_data


def create_data_for_query(location: LocationData):
    data = {
        "lat": "-14.4833",
        "lng": "-75.2456",
        "accion": "Detalle",
        "ubicacion": "1",
        "s_departament_geo": location.region_code,
        "s_province_geo": location.province_code,
        "s_district_geo	": location.district_code,
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
    url = "https://identicole.minedu.gob.pe/colegio/busqueda_colegios_detalle"
    data = create_data_for_query(location=location)
    response = requests.post(url, data=data)
    location_name = (
        f"{location.region_name}-{location.province_name}-{location.district_name}"
    )
    status_code = response.status_code
    if status_code != 200:
        print(f"! Error al obtener colegios para {location_name} -> {status_code}")
        return
    process_school_query(
        location=location,
        connection=connection,
        text=response.text,
        location_name=location_name,
    )
    print(f"Se registraron los colegios para {location_name}")


def process_school_query(
    location: LocationData, connection, text: str, location_name: str
):
    parts = text.split("||")
    if len(parts) < 4:
        print(f"! No se encontraron colegios para {location_name}")
        return
    print(f"Se encontraron {parts[2]} colegios para {location_name}")
    schools = json.loads(parts[3])
    for school in schools:
        try:
            insert_school(
                connection=connection, json_data=school, location_data=location
            )
        except Exception as e:
            continue
    pagination_numbers = get_pagination_numbers(text=text)
    if pagination_numbers == 0:
        return
    for page in pagination_numbers:
        get_schools_pagination_data(location=location, page=page, connection=connection)


def get_pagination_numbers(text: str):
    soup = BeautifulSoup(text, "html.parser")
    pagination = soup.find("ul", class_="paginator")
    if pagination is None:
        return 0
    links = pagination.find_all("a", class_="paginacion-numerada")
    return list(set([link["data-nro-pagina"] for link in links]))


def get_schools_pagination_data(location: LocationData, page: int, connection):
    url = f"https://identicole.minedu.gob.pe/colegio/busqueda_colegios_detalle/{page}"
    data = create_data_for_query(location=location)
    response = requests.post(url, data=data)
    location_name = (
        f"{location.region_name}-{location.province_name}-{location.district_name}"
    )
    status_code = response.status_code
    if status_code != 200:
        print(f"! Error al obtener colegios para {location_name} -> {status_code}")
        return
    parts = response.text.split("||")
    if len(parts) < 4:
        print(f"! No se encontraron colegios para {location_name} - page {page}")
        return
    print(f"\tSe encontraron {parts[2]} colegios para {location_name} - page {page}")
    schools = json.loads(parts[3])
    for school in schools:
        try:
            insert_school(
                connection=connection, json_data=school, location_data=location
            )
        except Exception as e:
            continue


def main():
    connection = create_sql_connection()
    locations = get_departments_data(connection=connection)
    location_data: list[LocationData] = transform_location_data(locations=locations)
    for location in location_data:
        get_schools_data(location=location, connection=connection)


if __name__ == "__main__":
    main()
