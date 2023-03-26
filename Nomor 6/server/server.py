from bs4 import BeautifulSoup
import threading
import os
import sys
import socket
import select
import configparser


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

    # Concat response header
    def getResponseHeader(self, status_code, content_type, content_length):
        response_header = 'HTTP/1.1 '+status_code+'\r\nContent-Type: '+content_type+'; charset=UTF-8\r\nContent-Length:' \
            + str(content_length) + '\r\n\r\n'
        return response_header

    # Read file untuk HTML
    def readFile(self, file_name):
        f = open(file_name, 'r')
        response_data = f.read()
        f.close()
        return response_data

    # Show 404
    def viewNotFound(self):
        response_data = self.readFile('404.html')
        content_length = len(response_data)
        response_header = self.getResponseHeader(
            '404 Not Found', 'text/html', content_length)
        self.client.sendall(response_header.encode(
            'utf-8') + response_data.encode('utf-8'))

    # Move up one directory
    def moveBack(self, path):
        new_path = path.split("/")
        new_path.pop()
        new_path = "/".join(new_path)
        return new_path

    # SendFile buat download
    def sendFile(self, file_path):
        with open(file_path, 'rb') as f:
            data = f.read(self.size)
            while data:
                self.client.send(data)
                data = f.read(self.size)

    # Proses mengirim dan
    # menerima data
    def run(self):
        running = 1
        while running:
            # Terima request
            data = self.client.recv(self.size)
            print('received: ', self.address, data)

            # Olah header
            data = data.decode('utf-8')
            request_header = data.split('\r\n')

            # Ambil commandnya apa
            request_file = request_header[0].split()
            if len(request_file) > 1:
                request_file = request_file[1]

            response_header = b''
            response_data = b''

            # HELP
            if request_file == '/help' or request_file == 'help':
                response_data = ('<html><head><style>body{background-color: #FFC0D3;}</style></head>' +
                                 '<body><h1>Berikut merupakan command yang dapat digunakan: \n</h1>' +
                                 '<h3>~ /help : untuk melihat command tersedia - harus di root\n</h3>' +
                                 '<h3>~ / atau /index.html : untuk membuka index.html\n</h3>' +
                                 '<h3>~ /:nama directory : untuk pindah directory\n</h3>' +
                                 '<h3>~ /:nama file : untuk download file\n</h3>' +
                                 '<h3>~ /back : untuk kembali kedirectory sebelumnya\n</h3><a href="/">Back</a></body></html>')

                response_header = self.getResponseHeader(
                    '200 OK', 'text/html', len(response_data))
                self.client.sendall(response_header.encode(
                    'utf-8') + response_data.encode('utf-8'))

            # Cek ada tidaknya directory / file
            else:
                print(request_file)
                check_path = self.base_dir + ''.join(request_file)
                # Untuk request ke home/index.html
                if (request_file == '/' or request_file == 'index.html' or request_file == '/index.html'):
                    response_data = self.readFile('index.html')
                    content_length = len(response_data)

                    response_header = self.getResponseHeader(
                        '200 OK', 'text/html', content_length)
                    self.client.sendall(response_header.encode(
                        'utf-8') + response_data.encode('utf-8'))

                # Cek kalo semisal directory nanti langsung change directory
                elif os.path.exists(check_path) and os.path.isdir(check_path) and request_file[-1] != '/':
                    print(request_file)
                    current_dir = check_path
                    response_data = (current_dir.split(self.base_dir)[1])
                    content_length = len(response_data)

                    response_header = self.getResponseHeader(
                        '200 OK', 'text/dir', content_length)
                    self.client.sendall(response_header.encode(
                        'utf-8') + response_data.encode('utf-8'))

                # Cek kalo semisal dia ternyata file
                elif os.path.isfile(check_path):
                    file_path = check_path
                    content_length = os.path.getsize(file_path)
                    file_extention = file_path.split('.')[-1]

                    response_header = self.getResponseHeader(
                        '200 OK', 'application/' + file_extention, content_length)
                    self.client.send(response_header.encode('utf-8'))
                    self.sendFile(file_path)

                # Untuk print daftar isi directory saat tidak ada file
                elif self.moveBack(check_path) == self.dataset_dir or check_path == self.dataset_dir:
                    dir_list = os.listdir(self.moveBack(check_path))

                    def linkList(dir):
                        return '<li><a href="/dataset/'+dir+'">'+dir+'</a></li>'

                    dir_list = list(map(linkList, dir_list))
                    dir_list = '\n'.join(dir_list)
                    dir_list = '<html><head><style>body{background-color: #FFC0D3;}</style></head><body><h1>Data yang tersedia di Dataset:</h1><ul>' + \
                        dir_list+'</ul><a href="/">Back</a></body></html>'
                    # soup = BeautifulSoup(dir_list, 'html.parser')
                    # a_tag = soup.find('a')
                    # url = a_tag.get('href')
                    # print(url)

                    response_header = self.getResponseHeader(
                        '404 Not Found', 'text/html', len(dir_list))
                    self.client.sendall(response_header.encode(
                        'utf-8') + dir_list.encode('utf-8'))

                # Apabila tidak ada semua menampilkan notfound
                else:
                    self.viewNotFound()

            self.client.close()
            running = 0


if __name__ == "__main__":
    server = Server()
    server.run()
