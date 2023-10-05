import hashlib
import json
import socket

requests_data = {}

server_address = ("127.0.0.1", 12345)


# Функція для аутентифікації на сервері
def authenticate(username, password):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_address)

        # Хешування паролю перед відправкою на сервер
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Відправка ім'я користувача та хеш-значення паролю на сервер
        auth_data = json.dumps({"credentials": f"{username}:{hashed_password}"})
        client_socket.send(auth_data.encode("utf-8"))

        response = client_socket.recv(1024)
        response.decode()
        client_socket.close()

        return response
    except Exception as e:
        print(f"Authentication error: {str(e)}")


def login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    response = json.loads(authenticate(username, password))
    if response.get("status") == 200:
        print("Successfully logged in!")
        requests_data["logged_user"] = username
    else:
        print(response)


def read():
    key = input("Enter key what to read: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    requests_data["data"] = {}
    requests_data["action"] = "read"
    requests_data["data"]["key"] = key
    client_socket.send(json.dumps(requests_data).encode("utf-8"))
    response = json.loads(client_socket.recv(1024).decode("utf-8"))
    del requests_data["action"]
    requests_data["data"] = {}
    print(response)
    client_socket.close()
    return


def write():
    key = input("Enter key what to write: ")
    value = input("Enter value that you want to write: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    requests_data["data"] = {}
    requests_data["action"] = "write"
    requests_data["data"]["key"] = key
    requests_data["data"]["value"] = value
    client_socket.send(json.dumps(requests_data).encode("utf-8"))
    response = json.loads(client_socket.recv(1024).decode())
    del requests_data["action"]
    requests_data["data"] = {}
    print(response)
    client_socket.close()
    return


def finish():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    client_socket.send(json.dumps({"final_move": True}).encode("utf-8"))
    client_socket.close()
    return


# Головна функція клієнта
def main():
    while True:
        action = input("Enter your action: ")

        if action == "login":
            login()

        if action == "read":
            if not requests_data.get("logged_user", None):
                print("You need to login.")
            else:
                read()

        if action == "write":
            if not requests_data.get("logged_user", None):
                print("You need to login.")
            else:
                write()

        if action == "logout":
            del requests_data["logged_user"]
            print("Successfully logged out.")

        if action == "finish":
            finish()
            break


if __name__ == "__main__":
    main()
