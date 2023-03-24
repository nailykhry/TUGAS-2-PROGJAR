import sys
import socket
import configparser

from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('httpclient.conf')

# mengambil data port dan host
port = config['server']['port']
host = config['server']['host']


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

            response = ''
            while True:
                received = client.recv(1024)
                if not received:
                    break
                response += received.decode('utf-8')

            if(e == 'help' or e == '/help'):
                print(response)
            else:
                soup = BeautifulSoup(response, 'html.parser')
                print(soup.title.string)
                print(soup.get_text())
            client.shutdown(socket.SHUT_RDWR)
            client.close()

    except Exception as msg:
        print(msg)


if __name__ == "__main__":
    main(sys.argv[1:])
