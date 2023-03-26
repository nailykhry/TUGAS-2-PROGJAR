# Dapatkanlah daftar menu pada halaman utama classroom.its.ac.id dengan melakukan parsing HTML

import socket
import ssl
from bs4 import BeautifulSoup

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
            data = ssock.recv(4096)
            if not data:
                break
            response += data
            soup = BeautifulSoup(response, 'html.parser')
        navbar = soup.find('nav', attrs={'class': 'navbar'})
        if navbar is not None:
            menu_items = navbar.find_all(
                'a', class_=['nav-link', 'dropdown-item'])
            if menu_items:
                check = ['dropdown-item']
                for item in menu_items[:-1]:
                    if item['class'] == check:
                        print('\t' + item.text.strip())
                    else:
                        print(item.text.strip())
            else:
                print('Menu tidak ditemukan.')
        else:
            print('Navbar tidak ditemukan.')
