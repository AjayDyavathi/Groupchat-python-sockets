from socket import *
import logging, time, selectors, pickle, datetime

HOST = gethostname()
# HOST = 'SERVR IP ADDRESS'
PORT = 40404

class Server():
    def __init__(self, host, port):

        self.main_socket = socket(AF_INET, SOCK_STREAM)
        self.main_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.main_socket.bind((host, port))
        self.main_socket.setblocking(False)
        self.main_socket.listen(100)

        self.selector = selectors.DefaultSelector()
        self.selector.register(self.main_socket, selectors.EVENT_READ, data=self.on_accept)

    current_peers = {}
    connections = {}


    def on_accept(self, sock, mask):
        # this is a handler for main socket

        conn, addr = self.main_socket.accept()
        print(f'accepted connection from {addr}')
        conn.setblocking(False)
        
        name = conn.recv(1024).decode()

        self.connections[conn] = name + f':\t({str(datetime.datetime.now().time())[:5]})'
        active = pickle.dumps(list(self.connections.values()))

        for each in self.connections:
            each.send(f'[NEW CONNECTION]:\t\t\t{name} joined this group\n'.encode()+active)
        
        self.current_peers[conn.fileno()] = conn.getpeername()
        self.selector.register(conn, selectors.EVENT_READ, data=self.on_read)


    def on_read(self, conn, mask):
        # this is a handler for peer sockets
        try:
            data = conn.recv(1024)
            if data:
                peername = conn.getpeername()
                print(f'got data from {peername}: {data}')

                name = '[' + self.connections[conn].split(':')[0] + ']: '
                for each in self.connections:
                    each.send(name.encode()+data)
                print(f'sent data: {data}')

            else:
                self.close_connection(conn)

        except ConnectionResetError:
            self.close_connection(conn)

    def close_connection(self, conn):
        
        name = self.connections[conn].split(':')[0]
        del self.connections[conn]
        active = pickle.dumps(list(self.connections.values()))

        for each in self.connections:
            each.send(f'[DISCONNECTED]:\t\t\t{name} has left this group\n'.encode()+active)

        peername = self.current_peers[conn.fileno()]
        print(f'Closing connection to {peername}')
        del self.current_peers[conn.fileno()]
        
        self.selector.unregister(conn)
        conn.close()

    def serve_forever(self):
        while True:
            self.events = self.selector.select(timeout=0.2)

            for key, mask in self.events:
                handler = key.data
                handler(key.fileobj, mask)



if __name__ == '__main__':
    print('Starting server...')
    server = Server(host=HOST, port=PORT)
    server.serve_forever()



