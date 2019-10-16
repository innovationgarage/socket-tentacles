# Socket tentacles

Simple thread based tcp client/server that divorces the concept of
server/client from which side opens the tcp connection. Configured
using a simple dictionary structure that can be easily read from json.

Example usage

    import socket_tentacles

    class ReceiveHandler(socket_tentacles.ReceiveHandler):
        def handle(self):
            for line in self.file:
                # Do something to line here

    class SendHandler(socket_tentacles.SendHandler):
        def handle(self):
            while True:
                line = magic_global_send_queue.get()
                self.file.write(line)
                self.file.flush()

    if __name__ == "__main__":
        with open(sys.argv[1]) as f:
            config = json.load(f)

        server = socket_tentacles.Server({"source": ReceiveHandler, "destination": SendHandler})
        server.configure(config)

Example config.json:

    {
        "connections": [
            {"handler": "source", "type": "listen", "address": "tcp:1024"},
            {"handler": "destination", "type": "listen", "address": "tcp:1025"},
            {"handler": "destination", "type": "connect", "address": "tcp:localhost:1026"}
        ]
    }

Note: configure() can be called multiple times. A later applied configuration overrides a previously
applied one. However, already established tcp connections are not closed.
