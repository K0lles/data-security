import socket
import hashlib


# Функція для аутентифікації на сервері
def authenticate(username, password):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('127.0.0.1', 12345)
        client_socket.connect(server_address)

        # Хешування паролю перед відправкою на сервер
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Відправка ім'я користувача та хеш-значення паролю на сервер
        auth_data = f"{username}:{hashed_password}".encode()
        client_socket.send(auth_data)

        response = client_socket.recv(1024)
        print(response.decode())

        client_socket.close()
    except Exception as e:
        print(f"Authentication error: {str(e)}")


# Головна функція клієнта
def main():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    authenticate(username, password)


if __name__ == '__main__':
    main()
