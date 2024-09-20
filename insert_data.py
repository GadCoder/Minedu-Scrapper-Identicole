import os
import json
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def create_sql_connection():
    connection = mysql.connector.connect(
        host=os.getenv("host"),  # e.g., "localhost"
        user=os.getenv("user"),  # e.g., "root"
        password=os.getenv("password"),
        database=os.getenv("database"),
    )
    return connection


def insert_region(connection, name: str, code: str):
    insert_query = """
    INSERT INTO region (name, code) 
    VALUES (%s, %s)
    """
    values = (name, code)
    cursor = connection.cursor()
    cursor.execute(insert_query, values)
    connection.commit()  # Commit the transaction


def insert_province(connection, name: str, code: str, region_code: str):
    insert_query = """
    INSERT INTO province (name, code, province_code, region_code) 
    VALUES (%s, %s, %s, %s)
    """
    values = (name, f"{region_code}.{code}", code, region_code)
    cursor = connection.cursor()
    cursor.execute(insert_query, values)
    connection.commit()  # Commit the transaction


def insert_district(
    connection, name: str, code: str, province_code: str, region_code: str
):
    insert_query = """
    INSERT INTO district (name, code, district_code, province_code) 
    VALUES (%s, %s, %s, %s)
    """
    values = (
        name,
        f"{region_code}.{province_code}.{code}",
        code,
        f"{region_code}.{province_code}",
    )
    cursor = connection.cursor()
    cursor.execute(insert_query, values)
    connection.commit()  # Commit the transaction


def main():
    connection = create_sql_connection()
    with open("data_departments.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    for department in data["departments"]:
        insert_region(connection, department["name"], department["value"])
        for province in department["provinces"]:
            insert_province(
                connection, province["nombre"], province["codprov"], department["value"]
            )
            for district in province["districts"]:
                insert_district(
                    connection,
                    district["nombre"],
                    district["coddist"],
                    province["codprov"],
                    department["value"],
                )


if __name__ == "__main__":
    main()
