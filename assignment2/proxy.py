#!/usr/bin/python

import socket
import os
from threading import Thread


class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.temperature = None # temperature client socket not known yet
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    # run in thread
    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                try:
                    print("[From server      ] {}".format(str(data,'utf-8')))
                except Exception as e:
                    print(e)
                # forward to client
                self.temperature.sendall(data)

class Temperature2Proxy(Thread):

    def __init__(self, host, port):
        super(Temperature2Proxy, self).__init__()
        self.server = None # real server socket not known yet
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        # waiting for a connection
        self.temperature, addr = sock.accept()

    def run(self):
        while True:
            data = self.temperature.recv(4096)
            if data:
                try:
                    print("[From Raspberry pi] {}".format(str(data,'utf-8')))
                except Exception as e:
                    print(e)
                # forward to server
                self.server.sendall(data)

class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("Setting up")
            self.g2p = Temperature2Proxy(self.from_host, self.port) # waiting for a client
            self.p2s = Proxy2Server(self.to_host, self.port)
            print("Connection established")
            self.g2p.server = self.p2s.server
            self.p2s.temperature = self.g2p.temperature

            self.g2p.start()
            self.p2s.start()


proxy_server = Proxy('0.0.0.0', '130.236.81.13', 8718)
proxy_server.start()



while True:
    try:
        cmd = input('$ ')
        if cmd[:4] == 'quit':
            os._exit(0)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception as e:
        print(e)