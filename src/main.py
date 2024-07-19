from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive, stream_receive

from cvg_core.procedures.crypto_send_and_receive import crypto_exchange, crypto_send_and_receive, crypto_send, crypto_receive

def client_test():    
    connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER
    )
    
    sleep(2)
    
    connection.socket.connect(connection.address)
    
    crypto_exchange(connection)
    response = crypto_send_and_receive(
        connection,
        PacketObject(
            b"Hello there! -client",
            PacketType.GATEWAY
        )
    )
    
    sleep(0.1)
    
    print("[crypto-receive]", response)
    

def server_test():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    
    connection = ConnectionObject(
        *server_socket.accept(), 
        type=ConnectionType.SERVER_TO_CLIENT
    )
    
    test_packet = PacketObject(
        b"Hello! -server",
        PacketType.GATEWAY
    )   
    
    crypto_exchange(connection)
    packet = crypto_receive(connection)
    
    test_packet.id = packet.id
    
    crypto_send(connection, test_packet)
    
    print("[server-receive]", packet)


Thread(target=server_test).start()
client_test()
