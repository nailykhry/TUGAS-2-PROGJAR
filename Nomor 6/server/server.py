import configparser
import select
import socket
import sys
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

    # fungsi untuk handle request
    def handle_request(self, data):
        data = data.decode('utf-8')
        return data.encode('utf-8')

    # Proses mengirim dan
    # menerima data
    def run(self):
        running = 1
        while running:
            data = self.client.recv(self.size)
            print('received: ', self.address, data)

            response = self.handle_request(data)
            if data:
                self.client.send(response)
            else:
                self.client.close()
                running = 0


if __name__ == "__main__":
    server = Server()
    server.run()
