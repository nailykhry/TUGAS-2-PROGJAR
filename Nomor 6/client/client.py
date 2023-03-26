import socket
import configparser
import os


from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('httpclient.conf')

# mengambil data port dan host
port = config['server']['port']
host = config['server']['host']


def getHeader(client):
    header = b''
    while True:
        data = client.recv(1024)
        header += data
        if b'\r\n\r\n' in header:
            break
    header = header.decode('utf-8')
    return header


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


def getContentType(res):
    type = res.split('Content-Type: ')[1].split(';')[0]
    content_type = type.split('/')[0]
    content_type2 = type.split('/')[1]
    return content_type, content_type2


def getStatusCode(res):
    status_code = res.split()[1]
    return status_code


def getFileName(req):
    file_name = req.split('/')[2]
    return file_name


def getBody(client):
    response = ''
    while True:
        received = client.recv(1024)
        if not received:
            break
        response += received.decode('utf-8')
    return response


def printHTMLParser(response):
    soup = BeautifulSoup(response, 'html.parser')
    print(soup.get_text())


def main():
    try:
        current_dir = '/'
        while True:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, int(port)))
            print('\nCurrent Working Directory: ' + current_dir)
            e = input("Masukkan URN atau ketik 'CTRL+C' untuk keluar: ")

            # untuk clear history sebelumnya
            os.system('cls||clear')

            if e == 'back' or e == '/back':
                if current_dir != '/':
                    current_dir = current_dir.split("/")
                    current_dir.pop()
                    current_dir = "/".join(current_dir)
                    if current_dir == '':
                        current_dir = '/'
                client.shutdown(socket.SHUT_RDWR)
                client.close()
                continue

            if current_dir != '/':
                e = current_dir + e
            request_header = ("GET " +
                              e +
                              " HTTP/1.1\r\n" +
                              "Host: " +
                              host + "\r\n" +
                              "\r\n").encode('utf-8')

            client.send(request_header)
            header = getHeader(client)

            status_code = getStatusCode(header)
            content_type, content_type2 = getContentType(header)
            if status_code == '200':

                if content_type2 == 'dir':
                    response = getBody(client)
                    response = header + response
                    response = response.split('\r\n')[-1]
                    current_dir = response
                elif content_type == 'application':
                    file_name = getFileName(e)
                    getFile(client, file_name)
                    print(header)
                else:
                    response = getBody(client)
                    response = header + response
                    if content_type2 == 'html':
                        printHTMLParser(response)

                    else:
                        print(response)

            else:
                response = getBody(client)
                response = header + response
                if content_type2 == 'html':
                    printHTMLParser(response)

                else:
                    print(response)

    finally:
        client.shutdown(socket.SHUT_RDWR)
        client.close()


if __name__ == "__main__":
    main()
