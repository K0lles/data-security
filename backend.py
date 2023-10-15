import json
import socket
from typing import Any, Union, Tuple

import constants
from constants import ACCESS_FILE_PATH

saved_data: dict = {"base_data": "You have got BASE_DATA OKEY"}


def get_username_permission(username: str) -> list:
    with open(ACCESS_FILE_PATH, "r") as file:
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
        function_mapping = {"read": read, "write": write, "logs": logs}

        # Отримання ім'я користувача та геш-значення паролю від клієнта
        if username := data.get("logged_user", None):
            permissions: list = get_username_permission(username)
            print(f"user: {username}, permissions: {permissions}")
            if action := function_mapping.get(data.get("action", None), None):
                function_data: dict = data.get("data", {})
                print(f"function_data: {function_data}")
                status, response = action(permissions=permissions, **function_data)
                log_action(f"{status}|{action.__name__}|{username}\n")
                client_socket.send(json.dumps(response).encode("utf-8"))
                return True

        else:
            if data.get("action", None) == "sign_up":
                status, response = sign_up(
                    data.get("username", ""), data.get("password", "")
                )
                log_action(f"{status}|sign_up|{data.get('username', '')}\n")
                client_socket.send(json.dumps(response).encode("utf-8"))
                return True
            username, hashed_password = data.get("credentials", "").split(":")
            # Перевірка аутентифікації на основі флеш-диска
            if check_authentication_on_flash_drive(username, hashed_password):
                response = json.dumps({"status": 200})
                log_action(f"True|login|{username}\n")
                client_socket.send(response.encode("utf-8"))
                return True
            else:
                response = json.dumps({"status": 400})
                log_action(f"False|login|{username}\n")
                client_socket.send(response.encode("utf-8"))
                return False

    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False


def log_action(action: str) -> None:
    with open(constants.LOG_PATH, "a") as log_file:
        log_file.write(action)


def logs(permissions: list, username: str) -> any:
    if not "READ" in permissions:
        return False, ["You do not have permission."]
    response = []
    with open(constants.LOG_PATH, "r") as logs:
        lines = logs.readlines()
        for line in lines:
            if line.split("|")[2].replace("\n", "") == username:
                response.append(line)
    return True, response


def sign_up(username: str, password: str) -> Tuple[bool, str]:
    if not username or not password:
        return False, "Write correct username or password"

    with open(ACCESS_FILE_PATH, "r") as file:
        lines: list[str] = file.readlines()
        for line in lines:
            (
                stored_username,
                stored_hashed_password,
                permissions,
            ) = line.strip().split(":")
            if stored_username == username:
                return (
                    False,
                    "This username is already in use. Make up something unique.",
                )

    if validate_username(username):
        with open(ACCESS_FILE_PATH, "a") as file:
            file.write(
                f"\n{username}:{password}:{','.join(constants.SIGN_UP_PERMISSION)}"
            )

    return True, "Successfully signed up."


def validate_username(username: str) -> bool:
    if (
        len(username) > 4
        and not username.__contains__(" ")
        and not username.__contains__("|")
    ):
        return True
    return False


def read(key: any, permissions: list = None) -> any:
    if "READ" in permissions:
        return True, saved_data.get(key, None)
    return False, "You do not have permission."


def write(key: any, value: any, permissions: list = None) -> any:
    if "WRITE" in permissions:
        try:
            saved_data[key] = value
            return True, saved_data.get(key)
        except Exception as exc:
            print(f"Error has occurred with writing in database." f"{exc}")
        return False, None
    return False, "You do not have permission."


# Функція для перевірки аутентифікації на основі флеш-диска
def check_authentication_on_flash_drive(username: str, hashed_password: str) -> bool:
    try:
        # Відкрийте файл на флеш-диску для перевірки аутентифікації
        # Файл повинен містити інформацію про користувачів та їх хеш-значення паролів
        with open(ACCESS_FILE_PATH, "r") as file:
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
