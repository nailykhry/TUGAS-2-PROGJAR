from inspect import getfile
import sys
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


def main(elements):
    try:
        for e in elements:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, int(port)))
            # client.send(bytes(e+'\r\n', encoding='utf-8'))

            request_header = ("GET " +
                              e +
                              " HTTP/1.1\r\n" +
                              "Host: " +
                              host + "\r\n" +
                              "Connection: close\r\n" +
                              "\r\n").encode('utf-8')

            client.send(request_header)
            header = getHeader(client)

            status_code = getStatusCode(header)
            if(status_code == '200'):
                content_type, content_type2 = getContentType(header)

                if(content_type == 'application'):
                    file_name = getFileName(e)
                    getFile(client, file_name)
                else:
                    response = getBody(client)
                    response = header + response
                    if content_type2 == 'html':
                        soup = BeautifulSoup(response, 'html.parser')
                        print(soup.title.string)
                        print(soup.get_text())

                    else:
                        print(response)
            else:
                content_type, content_type2 = getContentType(header)
                response = getBody(client)
                response = header + response
                if content_type2 == 'html':
                    soup = BeautifulSoup(response, 'html.parser')
                    print(soup.title.string)
                    print(soup.get_text())

                else:
                    print(response)

        client.shutdown(socket.SHUT_RDWR)
        client.close()

    except Exception as msg:
        print(msg)


if __name__ == "__main__":
    main(sys.argv[1:])
