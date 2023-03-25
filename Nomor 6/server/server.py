import configparser
import select
import socket
import sys
import os
import threading


# membaca file konfigurasi
config = configparser.ConfigParser()
config.read('httpserver.conf')

# mengambil data port dan host
port = config['server']['port']
host = config['server']['host']


class Server:
    # inisialisasi variabel
    def __init__(self):
        self.host = host
        self.port = int(port)
        self.backlog = 5
        self.size = 1024
        self.server = None
        self.threads = []

    # membuat socket, bind, listen

    def open_socket(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

    def run(self):
        self.open_socket()
        input_list = [self.server, sys.stdin]
        running = 1
        while running:

            # Pengecekan modul select
            input_ready, _, _ = select.select(input_list, [], [])

            for s in input_ready:

                if s == self.server:
                    # handle the server socket
                    client_socket, client_address = self.server.accept()

                    # Jika ada klien terkoneksi,
                    # buat instance kelas Client yang dibuat
                    # dari parent kelas thread
                    c = Client(client_socket, client_address)
                    c.start()
                    self.threads.append(c)

                elif s == sys.stdin:
                    # handle standard input
                    _ = sys.stdin.readline()
                    running = 0

        # close all threads
        # Memastikan semua thread klien sudah selesai menjalankan tugasnya
        self.server.close()
        for c in self.threads:
            c.join()


# Kelas Client diturunkan dari kelas threading.Thread
class Client(threading.Thread):
    def __init__(self, client, address):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 1024

    def isFileExist(self, file_name):
        path = os.getcwdb().decode('utf-8')
        path = os.path.join(path, 'dataset')
        dir_list = os.listdir(path)
        if file_name in dir_list:
            return True
        return False

    def sendFile(self, file_path):
        print('File Send Successfully')

    # Proses mengirim dan
    # menerima data
    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            print('received: ', self.address, data)

            data = data.decode('utf-8')
            request_header = data.split('\r\n')
            request_file = request_header[0].split()
            if len(request_file) > 1:
                request_file = request_file[1]
            response_header = b''
            response_data = b''

            # HELP
            if request_file == '/help' or request_file == 'help':
                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=UTF-8\r\n' \
                    + '\r\n\r\n'

                response_data = ('Berikut merupakan command yang dapat digunakan: \n\n' +
                                 '~ /help : untuk melihat command tersedia\n' +
                                 '~ / atau /index.html : untuk membuka index.html\n' +
                                 '~ /dataset  : melihat daftar isi dari dataset\n' +
                                 '~ /dataset/:nama file : untuk mendownload file tertentu\n')

                self.client.sendall(response_header.encode(
                    'utf-8') + response_data.encode('utf-8'))

            # INDEX HTML
            elif request_file == '/' or request_file == '/index.html':
                f = open('index.html', 'r')
                response_data = f.read()
                f.close()

                content_length = len(response_data)
                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                    + str(content_length) + '\r\n\r\n'

                self.client.sendall(response_header.encode(
                    'utf-8') + response_data.encode('utf-8'))

            # LIST DIRECTORY / DATASET
            elif request_file == '/dataset':
                path = os.getcwdb().decode('utf-8')
                path = os.path.join(path, 'dataset')
                dir_list = os.listdir(path)
                dir_list = '\n'.join(dir_list)
                response_header = 'HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=UTF-8' \
                    + '\r\n\r\n'

                self.client.sendall(response_header.encode(
                    'utf-8') + dir_list.encode('utf-8'))

            elif request_file.split('/')[1] == 'dataset':
                file_name = request_file.split('/')[2]
                if self.isFileExist(file_name):
                    # Download file
                    file_path = 'dataset/' + file_name
                    content_length = os.path.getsize(file_path)
                    response_header = 'HTTP/1.1 200 OK\r\nContent-Type: application/zip; charset=UTF-8\r\nContent-Length:' \
                        + str(content_length) + '\r\n\r\n'
                    self.client.send(response_header.encode('utf-8'))
                    with open(file_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            self.client.send(data)
                            data = f.read(1024)
                else:
                    f = open('404.html', 'r')
                    response_data = f.read()
                    f.close()

                    content_length = len(response_data)
                    response_header = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                        + str(content_length) + '\r\n\r\n'

                    self.client.sendall(response_header.encode(
                        'utf-8') + response_data.encode('utf-8'))

            else:

                f = open('404.html', 'r')
                response_data = f.read()
                f.close()

                content_length = len(response_data)
                response_header = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length:' \
                    + str(content_length) + '\r\n\r\n'

                self.client.sendall(response_header.encode(
                    'utf-8') + response_data.encode('utf-8'))

            self.client.close()
            running = 0


if __name__ == "__main__":
    server = Server()
    server.run()
