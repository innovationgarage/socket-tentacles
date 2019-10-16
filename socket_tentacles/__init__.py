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
        
class Listener(threading.Thread):
    def run(self):
        kwargs = self._kwargs
        print("Listener: Started: %s" % kwargs)
        Handler = self._kwargs["handler"]
        server = self._kwargs["server"]
        class Server(socketserver.BaseRequestHandler):
            def handle(self):
                print("Listener: Connection request received: %s" % kwargs)
                Handler(server, self.request)
        self.server = TCPServer((kwargs["host"], kwargs["port"]), Server)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        
class Connector(threading.Thread):
    def __init__(self, *arg, **kw):
        self.is_stopping = False
        threading.Thread.__init__(self, *arg, **kw)
    def run(self):
        print("Connector: Started: %s" % self._kwargs)
        while not self.is_stopping:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                try:
                    sock.connect((self._kwargs["host"], self._kwargs["port"]))
                    print("Connector: Connected: %s" % self._kwargs)
                    self._kwargs["handler"](self._kwargs["server"], sock)
                except Exception as e:
                    print(e)
            finally:
                sock.close()
            time.sleep(1)
    def stop(self):
        self.is_stopping = True
        
class Handler(object):
    encoding = "utf-8"
    binary = False
    filemode = "r"
    
    def __init__(self, server, conn):
        self.server = server
        self.conn = conn
        self.makefile()
        self.handle()
        
    def makefile(self):
        args = {"mode": self.filemode + ["", "b"][self.binary]}
        if not self.binary:
            args["encoding"] = self.encoding
        self.file = self.conn.makefile(**args)
        
    def handle(self):
        """self.conn is a socket object, self.file a file wrapper for that
        socket"""

    def __hash__(self):
        return id(self)

class ReceiveHandler(Handler):
    filemode = "r"
    
class SendHandler(Handler):
    filemode = "w"
        

class Server(object):
    def __init__(self, handlers):
        self.handlers = handlers
        self.config = None
        self.servers = {}

    def configure(self, config):
        self.config = config

        connections = {self.connection_key(connection): connection for connection in config["connections"]}
        to_create = connections.keys() - self.servers.keys()
        to_destroy = self.servers.keys() - connections.keys()
        
        for key in to_create:
            server = self.start_connection(connections[key])
            server.start()
            self.servers[key] = server

        for key in to_destroy:
            server = self.servers.pop(key)
            server.stop()
            
    def connection_key(self, connection):
        return json.dumps(connection, sort_keys=True, separators=(',', ':'))
            
    def start_connection(self, connection):
        handler = self.handlers[connection["handler"]]
        addr = connection["address"].split(":")
        assert addr[0] == "tcp"
        host = "0.0.0.0"
        port = 1024
        if len(addr) == 2:
            port = addr[1]
        if len(addr) == 3:
            host, port = addr[1:]
        port = int(port)
        connhandler = {"listen": Listener, "connect": Connector}[connection["type"]]
        return connhandler(kwargs={"server": self, "host": host, "port": port, "handler": handler})

def run(config, handlers):
    server = Server(handlers)
    server.configure(config)
    return server
