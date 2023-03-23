# Cetaklah property charset pada Content-Type dari HTTP response header pada halaman classroom.its.ac.id
from email import charset
import socket
import ssl

hostname = 'classroom.its.ac.id'
context = ssl.create_default_context()
with socket.create_connection((hostname, 443)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        ssock.sendall(b"GET / HTTP/1.1\r\n"
                      b"Host: classroom.its.ac.id\r\n"
                      b"Connection: close\r\n"
                      b"\r\n")
        response = b''
        while True:
            data = ssock.recv(1024)
            if not data:
                break
            response += data
        response = response.decode("utf-8")
        propCharset = response.split(
            'charset=')[1].split('\r\n')[0]
        print(propCharset)
