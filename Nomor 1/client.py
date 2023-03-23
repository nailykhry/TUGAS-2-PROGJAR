# Cetaklah status code dan deskripsinya dari HTTP response header pada halaman its.ac.id
import socket
import ssl

# Untuk its.ac.id menghasilkan 301 Moved Permanently
# Untuk www.its.ac.id menghasilkan 200
hostname = 'www.its.ac.id'
context = ssl.create_default_context()
with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        ssock.sendall(b"GET / HTTP/1.1\r\n"
                      b"Host: www.its.ac.id\r\n"
                      b"Connection: close\r\n"
                      b"\r\n")
        response = b''
        while True:
            data = ssock.recv(1024)
            if not data:
                break
            response += data
        response = response.decode("utf-8")
        response_header = response.split('\r\n')[0]
        status_code = response_header.split()[1:]
        status_code = " ".join(status_code)
        print(status_code)
