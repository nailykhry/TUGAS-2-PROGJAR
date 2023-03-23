# Cetaklah versi Content-Encoding dari HTTP response header di halaman web its.ac.id
import socket
import ssl

# Untuk its.ac.id menghasilkan 301 Moved Permanently
# Untuk www.its.ac.id menghasilkan 200 OK
hostname = 'www.its.ac.id'
context = ssl.create_default_context()
with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        ssock.sendall(b"GET / HTTP/1.1\r\n"
                      b"Host: www.its.ac.id\r\n"
                      b"Accept-Encoding: br, gzip\r\n"
                      b"Connection: close\r\n"
                      b"\r\n")
        response = b''
        response = ssock.recv(600)
        response = response.decode("utf-8")
        content_encoding = response.split(
            'Content-Encoding: ')[1].split('\r\n')[0]
        print(content_encoding)
