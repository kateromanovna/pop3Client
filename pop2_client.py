import base64
import socket
import ssl

def request(socket, request):
    socket.send(request + b'\n')
    data = socket.recv(65535)
    return data.decode()

def request_stat(socket, request):
    socket.send(request + b'\n')
    recv_data = b''
    while True:
        data = socket.recv(1024)
        recv_data += data
        if not data or b'\n' in recv_data:
            break
    return recv_data.decode()

def download_attachment(socket, message_number, attachment_number):
    response = request(socket, b'RETR ' + bytes(str(message_number), 'utf-8'))
    lines = response.splitlines()
    print(lines)
    boundary = None
    for line in lines:
        if line.startswith('Content-Type: multipart/mixed; boundary='):
            boundary = line.split(b'boundary=')[1].decode()
            break
    if boundary:
        parts = response.split(b'--' + bytes(boundary, 'utf-8'))
        attachment = parts[attachment_number].split(b'\r\n\r\n')[1]
        with open(f'attachment_{message_number}_{attachment_number}.jpg', 'wb') as file:
            file.write(base64.b64decode(attachment))

host_addr = 'pop.yandex.ru'
port = 995
user_name = 'katemp3'
password = ''
base64login = base64.b64encode(user_name.encode()).decode()
base64password = base64.b64encode(password.encode()).decode()

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host_addr, port))
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        client = context.wrap_socket(client)
        print(client.recv(1024))

        print(request(client, b'USER ' + bytes(user_name, 'utf-8')))
        print(request(client, b'PASS ' + bytes(password, 'utf-8')))
        count_of_messages = int(request_stat(client, b'STAT').split()[1])
        print('Messages: ' + str(count_of_messages))

        message_number = 1
        print(request(client, b'TOP ' + bytes(str(message_number), 'utf-8') + bytes(2)))

        attachment_number = 1
        download_attachment(client, message_number, attachment_number)

        print(request(client, b'QUIT'))