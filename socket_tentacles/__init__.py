import socketserver
import socket
import sys
import threading
import json
import queue
import time
import datetime

class TCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        
class Server(threading.Thread):
    def run(self):
        print("Server: Started: %s" % self._kwargs)
        Handler = self._kwargs["handler"]
        class Server(socketserver.BaseRequestHandler):
            def handle(self):
                print("Server: Connection request received")
                Handler(self.request)
        self.server = TCPServer((self._kwargs["host"], self._kwargs["port"]), Server)
        self.server.serve_forever()

class Connector(threading.Thread):
    def run(self):
        print("Connector: Started: %s" % self._kwargs)
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((self._kwargs["host"], self._kwargs["port"]))
                print("Connector: Connected")
                self._kwargs["handler"](sock)
            finally:
                sock.close()
            time.sleep(1)

class Handler(object):
    def __init__(self, conn):
        self.conn = conn

    def handle(self):
        """self.conn is a socket object, self.file a file wrapper for that
        socket"""

    def __hash__(self):
        return id(self)

class ReceiveHandler(Handler):
    def __init__(self, conn):
        self.file = conn.makefile("r")
        self.handle()
    
class SendHandler(Handler):
    def __init__(self, conn):
        self.file = conn.makefile("w")
        self.handle()
        
def parse_config(config, handlers):
    for connection in config["connections"]:
        handler = handlers[connection["direction"]]
        addr = connection["address"].split(":")
        assert addr[0] == "tcp"
        host = "0.0.0.0"
        port = 1024
        if len(addr) == 2:
            port = addr[1]
        if len(addr) == 3:
            host, port = addr[1:]
        port = int(port)
        connhandler = {"listen": Server, "connect": Connector}[connection["type"]]
        yield connhandler(kwargs={"host": host, "port": port, "handler": handler})

def run(config, handlers):
    for server in parse_config(config, handlers):
        server.start()
