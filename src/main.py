import sys

from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive, stream_receive
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange, crypto_send_and_receive, crypto_send, crypto_receive

from cvg_core.procedures.establish_connection import establish_connection

ENCRYPTION_ENABLED = False

big_password = b"cigarettes"*5000
print("password size", len(big_password))

def client_test():    
    sleep(1)
    
    connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER,
        encryption_enabled=ENCRYPTION_ENABLED
    )
    
    connection.socket.connect(connection.address)
    
    establish_connection(connection, big_password)
    
    sleep(0.1)
    
    print("[client] server established?", connection.established)



def server_test():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    
    connection = ConnectionObject(
        *server_socket.accept(), 
        type=ConnectionType.SERVER_TO_CLIENT,
        encryption_enabled=ENCRYPTION_ENABLED
    ) 
    
    establish_connection(connection, big_password)
    
    print("[server] client established?", connection.established)



if len(sys.argv) > 1:
    if sys.argv[1] == "client":
        client_test()
    elif sys.argv[1] == "server":
        Thread(target=server_test).start()
else:
    Thread(target=server_test).start()
    client_test()
