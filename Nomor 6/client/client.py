import socket
import configparser
import os


from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('httpclient.conf')

# mengambil data port dan host
port = config['server']['port']
host = config['server']['host']


# Mendapatkan header
def getHeader(client):
    header = b''
    while True:
        data = client.recv(1024)
        header += data
        if b'\r\n\r\n' in header:
            break
    header = header.decode('utf-8')
    return header


# Menyimpan hasil download
def getFile(client, file_name):
    if not os.path.exists('dataset'):
        os.mkdir('dataset')
    path = 'dataset/'+file_name
    with open(path, 'wb') as f:
        while True:
            data = client.recv(1024)
            if not data:
                break
            f.write(data)


# Mendapatkan content type
def getContentType(res):
    type = res.split('Content-Type: ')[1].split(';')[0]
    content_type = type.split('/')[0]
    content_type2 = type.split('/')[1]
    return content_type, content_type2


# Mendapatkan status code
def getStatusCode(res):
    status_code = res.split()[1]
    return status_code


# Mendapatkan filename
def getFileName(req):
    file_name = req.split('/')[2]
    return file_name


# Mendapatkan response bagian body
def getBody(client):
    response = ''
    while True:
        received = client.recv(1024)
        if not received:
            break
        response += received.decode('utf-8')
    return response


# Print hasil parsing
def printHTMLParser(response):
    soup = BeautifulSoup(response, 'html.parser')
    print(soup.get_text())


def main():
    try:
        current_dir = '/'
        while True:
            # Membangun koneksi
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, int(port)))

            # Print cwd
            print('\nCurrent Working Directory: ' + current_dir)

            e = input("Masukkan URN atau ketik 'CTRL+C' untuk keluar: ")

            # untuk clear history sebelumnya
            os.system('cls||clear')

            # Menangani setara cd ..
            if e == 'back' or e == '/back':

                # Kalau bukan di root
                if current_dir != '/':
                    current_dir = current_dir.split("/")
                    current_dir.pop()
                    current_dir = "/".join(current_dir)
                    e = '/'

                else:
                    print(
                        'Anda berada pada directory root, tidak dapat kembali kemanapun.')

            # Menambahkan command dengan current dir untuk menjadikan path
            if current_dir != '/':
                path = current_dir + e

            # Membuat request header dan mengirim ke server
            request_header = ("GET " +
                              path +
                              " HTTP/1.1\r\n" +
                              "Host: " +
                              host + "\r\n" +
                              "\r\n").encode('utf-8')
            client.send(request_header)

            # Mendapatkan response
            header = getHeader(client)
            status_code = getStatusCode(header)
            content_type, content_type2 = getContentType(header)

            # Untuk code dengan status_code 200
            if status_code == '200':
                # Hasilnya hanya pemindahan directory karena untuk pengecekan saja
                if content_type2 == 'dir':
                    response = getBody(client)
                    response = header + response
                    response = response.split('\r\n')[-1]
                    current_dir = response

                # Apabila download file
                elif content_type == 'application':
                    file_name = getFileName(e)
                    getFile(client, file_name)
                    print(header)

                # Response lainnya
                else:
                    response = getBody(client)
                    response = header + response
                    printHTMLParser(response)

            # Response saat 404
            else:
                response = getBody(client)
                response = header + response
                printHTMLParser(response)

    except KeyboardInterrupt:
        print("\n\nAnda menekan Ctrl+C maka program dihentikan... Sampai jumpa :(")

    finally:
        client.shutdown(socket.SHUT_RDWR)
        client.close()


if __name__ == "__main__":
    main()
