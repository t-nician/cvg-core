import sys

from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive, stream_receive

from cvg_core.procedures.crypto_send_and_receive import crypto_exchange, crypto_send_and_receive, crypto_send, crypto_receive

def client_test():    
    sleep(1)
    
    connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER
    )
    
    connection.socket.connect(connection.address)
    
    crypto_exchange(connection)
    
    response = crypto_send_and_receive(
        connection,
        PacketObject(
            b"hello",
            PacketType.GATEWAY
        )
    )
    
    sleep(0.1)
    
    print("[client-receive]", response)
    

def server_test():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    
    connection = ConnectionObject(
        *server_socket.accept(), 
        type=ConnectionType.SERVER_TO_CLIENT
    ) 
    
    crypto_exchange(connection)
    
    packet = crypto_receive(connection)
    
    crypto_send(
        connection, 
        PacketObject(
            b"hello",
            PacketType.GATEWAY
        )
    )
    
    print("[server-receive]", packet)

if len(sys.argv) > 1:
    if sys.argv[1] == "client":
        client_test()
    elif sys.argv[1] == "server":
        Thread(target=server_test).start()
else:
    Thread(target=server_test).start()
    client_test()
