import socket


# Функція для перевірки аутентифікації клієнта
def authenticate(client_socket: socket.socket) -> bool:
    try:
        # Приймання інформації від клієнта
        data = client_socket.recv(1024)
        if not data:
            return False

        # Отримання ім'я користувача та геш-значення паролю від клієнта
        username, hashed_password = data.decode().split(':')

        # Перевірка аутентифікації на основі флеш-диска
        if check_authentication_on_flash_drive(username, hashed_password):
            client_socket.send(b'Authentication successful')
            return True
        else:
            client_socket.send(b'Authentication failed')
            return False
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False


# Функція для перевірки аутентифікації на основі флеш-диска
def check_authentication_on_flash_drive(username: str, hashed_password: str) -> bool:
    try:
        # Відкрийте файл на флеш-диску для перевірки аутентифікації
        # Файл повинен містити інформацію про користувачів та їх хеш-значення паролів
        with open('d:/Users/VENTO/Desktop/Все на робочому столі/4 курс/Безпека даних/Лаборторна 7/flash-disk.txt', 'r') as file:
            lines: list[str] = file.readlines()
            for line in lines:
                stored_username, stored_hashed_password = line.strip().split(':')
                if username == stored_username and hashed_password == stored_hashed_password:
                    return True
    except Exception as e:
        print(f"Error checking authentication on flash drive: {str(e)}")
    return False


# Головна функція сервера
def main():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")

        authenticated = authenticate(client_socket)
        if authenticated:
            # Робіть тут щось з клієнтом, якщо аутентифікація успішна
            success_message = "Authentication was successful"
            client_socket.send(success_message.encode())

        else:
            client_socket.close()


if __name__ == '__main__':
    main()
