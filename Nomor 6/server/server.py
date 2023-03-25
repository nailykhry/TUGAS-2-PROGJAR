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
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.dataset_dir = self.base_dir + '/dataset'

    def isFileExist(self, file_name):
        path = os.getcwdb().decode('utf-8')
        path = os.path.join(path, 'dataset')
        dir_list = os.listdir(path)
        if file_name in dir_list:
            return True
        return False

    def getResponseHeader(self, status_code, content_type, content_length):
        response_header = 'HTTP/1.1 '+status_code+'\r\nContent-Type: '+content_type+'; charset=UTF-8\r\nContent-Length:' \
            + str(content_length) + '\r\n\r\n'
        return response_header

    def readFile(self, file_name):
        f = open(file_name, 'r')
        response_data = f.read()
        f.close()
        return response_data

    def viewNotFound(self):
        response_data = self.readFile('404.html')
        content_length = len(response_data)
        response_header = self.getResponseHeader(
            '404 Not Found', 'text/html', content_length)
        self.client.sendall(response_header.encode(
            'utf-8') + response_data.encode('utf-8'))

    def moveBack(self, path):
        new_path = path.split("/")
        new_path.pop()
        new_path = "/".join(new_path)
        return new_path

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
                response_data = ('Berikut merupakan command yang dapat digunakan: \n\n' +
                                 '~ /help : untuk melihat command tersedia\n' +
                                 '~ / atau /index.html : untuk membuka index.html\n' +
                                 '~ /back : untuk kembali kedirectory sebelumnya')

                response_header = self.getResponseHeader(
                    '200 OK', 'text/plain', len(response_data))

                self.client.sendall(response_header.encode(
                    'utf-8') + response_data.encode('utf-8'))

            # CHANGE DIRECTORY
            elif request_file.split()[0] == '/back' or request_file.split()[0] == 'back':
                if self.current_dir != self.base_dir:
                    self.current_dir = self.current_dir.split("/")
                    self.current_dir.pop()
                    self.current_dir = "/".join(self.current_dir)
                    if self.current_dir == '':
                        self.current_dir = '/'
                    response_data = (
                        'Berhasil berpindah ke - directory : ' + self.current_dir)
                else:
                    response_data = 'Anda berada pada root directory'
                content_length = len(response_data)
                response_header = self.getResponseHeader(
                    '200 OK', 'text/plain', content_length)

                self.client.sendall(response_header.encode(
                    'utf-8') + response_data.encode('utf-8'))

            # Cek ada tidaknya directory / file
            else:
                check_path = self.base_dir + request_file
                print(check_path)
                if request_file == '/' or request_file == 'index.html' or request_file == '/index.html':
                    f = open('index.html', 'r')
                    response_data = f.read()
                    f.close()

                    content_length = len(response_data)
                    response_header = self.getResponseHeader(
                        '200 OK', 'text/html', content_length)

                    self.client.sendall(response_header.encode(
                        'utf-8') + response_data.encode('utf-8'))

                elif os.path.exists(check_path) and os.path.isdir(check_path):
                    self.current_dir = check_path
                    response_data = (self.current_dir.split(self.base_dir)[1])
                    content_length = len(response_data)
                    response_header = self.getResponseHeader(
                        '200 OK', 'text/dir', content_length)
                    self.client.sendall(response_header.encode(
                        'utf-8') + response_data.encode('utf-8'))

                elif os.path.isfile(check_path):
                    file_path = check_path
                    content_length = os.path.getsize(file_path)
                    file_extention = file_path.split('.')[-1]
                    print(file_path)
                    print(request_file)
                    response_header = self.getResponseHeader(
                        '200 OK', 'application/' + file_extention, content_length)

                    self.client.send(response_header.encode('utf-8'))
                    with open(file_path, 'rb') as f:
                        data = f.read(self.size)
                        while data:
                            self.client.send(data)
                            data = f.read(self.size)

                elif self.moveBack(check_path) == self.dataset_dir:
                    dir_list = os.listdir(self.moveBack(check_path))
                    dir_list = '\n'.join(dir_list)

                    response_header = self.getResponseHeader(
                        '404 Not Found', 'text/plain', len(dir_list))

                    self.client.sendall(response_header.encode(
                        'utf-8') + dir_list.encode('utf-8'))

                else:
                    print(self.moveBack(check_path))
                    self.viewNotFound()

            self.client.close()
            running = 0


if __name__ == "__main__":
    server = Server()
    server.run()
