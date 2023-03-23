import sys
import socket
import configparser

# from urllib.request import urlopen
# from bs4 import BeautifulSoup

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
            client.send(bytes(e, encoding='utf-8'))
            # response = urlopen('http://www.python.org').read()
            # soup = BeautifulSoup(response)
            # print(soup.title.string)
            # print(soup.get_text())
            client.shutdown(socket.SHUT_RDWR)
            client.close()
    except Exception as msg:
        print(msg)


if __name__ == "__main__":
    main(sys.argv[1:])
