import json
import socket
from typing import Any, Union

from constants import FILE_PATH

saved_data: dict = {"base_data": "You have got BASE_DATA OKEY"}


def get_username_permission(username: str) -> list:
    with open(FILE_PATH, "r") as file:
        lines: list[str] = file.readlines()
        for line in lines:
            stored_username, stored_hashed_password, permissions = line.strip().split(
                ":"
            )
            permissions: list[str] = str(permissions).split(",")
            if username == stored_username:
                return permissions

    return []


# Функція для перевірки аутентифікації клієнта
def authenticate(
    client_socket: socket.socket, server_socket: socket.socket
) -> Union[bool, str]:
    try:
        # Приймання інформації від клієнта
        data = client_socket.recv(1024)
        if not data:
            return False

        data = json.loads(data.decode("utf-8"))
        if data.get("final_move", None):
            server_socket.close()
            return "Finish"

        print(data)
        function_mapping = {"read": read, "write": write}

        # Отримання ім'я користувача та геш-значення паролю від клієнта
        if username := data.get("logged_user", None):
            permissions: list = get_username_permission(username)
            print(f"user: {username}, permissions: {permissions}")
            if action := function_mapping.get(data.get("action", None), None):
                function_data: dict = data.get("data", {})
                print(function_data)
                print(action(permissions=permissions, **function_data))
                client_socket.send(
                    json.dumps(action(permissions=permissions, **function_data)).encode(
                        "utf-8"
                    )
                )
                return True

        else:
            username, hashed_password = data.get("credentials", "").split(":")
            # Перевірка аутентифікації на основі флеш-диска
            if check_authentication_on_flash_drive(username, hashed_password):
                response = json.dumps({"status": 200})
                client_socket.send(response.encode("utf-8"))
                return True
            else:
                response = json.dumps({"status": 400})
                client_socket.send(response.encode("utf-8"))
                return False

    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False


def read(key: any, permissions: list = None) -> any:
    if "READ" in permissions:
        return saved_data.get(key, None)
    return "You do not have permission."


def write(key: any, value: any, permissions: list = None) -> any:
    if "WRITE" in permissions:
        try:
            saved_data[key] = value
            return saved_data.get(key)
        except Exception as exc:
            print(f"Error has occurred with writing in database." f"{exc}")
        return None
    return "You do not have permission."


# Функція для перевірки аутентифікації на основі флеш-диска
def check_authentication_on_flash_drive(username: str, hashed_password: str) -> bool:
    try:
        # Відкрийте файл на флеш-диску для перевірки аутентифікації
        # Файл повинен містити інформацію про користувачів та їх хеш-значення паролів
        with open(FILE_PATH, "r") as file:
            lines: list[str] = file.readlines()
            for line in lines:
                (
                    stored_username,
                    stored_hashed_password,
                    permissions,
                ) = line.strip().split(":")
                if (
                    username == stored_username
                    and hashed_password == stored_hashed_password
                ):
                    return True
    except Exception as e:
        print(f"Error checking authentication on flash drive: {str(e)}")
    return False


# Головна функція сервера
def main():
    host = "127.0.0.1"
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        data = authenticate(client_socket, server_socket)

        if data == "Finish":
            print("Finishing socket.")
            break


if __name__ == "__main__":
    main()
