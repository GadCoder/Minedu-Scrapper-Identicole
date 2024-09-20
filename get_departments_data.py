import json
import base64
import requests


def load_departments():
    with open("departments_list.json", "r") as json_file:
        departments_list = json.load(json_file)
        return departments_list


def get_provinces(department_name: str, department_code: str):
    url = f"https://identicole.minedu.gob.pe/api/provincia/{department_code}"
    response = requests.post(url)
    status_code = response.status_code
    if status_code != 200:
        print(f"Error with {department_name}")

    jwt_token = response.text
    jwt_payload_encoded = jwt_token.split(".")[1]
    decoded_payload = base64.b64decode(jwt_payload_encoded + "==")
    response_data = json.loads(decoded_payload)
    return response_data


def get_districts(province_name: str, province_code: str, department_code: str):
    url = f"https://identicole.minedu.gob.pe/api/distrito/{department_code}/{province_code}"
    response = requests.post(url)
    status_code = response.status_code
    if status_code != 200:
        print(f"Error with {province_name}")
    jwt_token = response.text
    jwt_payload_encoded = jwt_token.split(".")[1]
    decoded_payload = base64.b64decode(jwt_payload_encoded + "==")
    response_data = json.loads(decoded_payload)
    return response_data


def main():
    departments_list = load_departments()
    for department in departments_list["departments"]:
        name = department["name"]
        department_code = department["value"]
        print(f"Getting info for {name}")
        department["provinces"] = get_provinces(
            department_name=name, department_code=department_code
        )
        for province in department["provinces"]:
            province_name = province["nombre"]
            province_code = province["codprov"]
            print(f"\tGetting info for {province_name}")
            province["districts"] = get_districts(
                province_name=province_name,
                province_code=province_code,
                department_code=department_code,
            )
    with open("departments_test.json", "w", encoding="utf-8") as json_file:
        json.dump(departments_list, json_file, indent=4)


if __name__ == "__main__":
    main()
