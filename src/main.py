import sys

from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.establish_connection import establish_connection

from cvg_core.procedures.command_send_and_receive import command_send_and_receive, command_receive_and_send

"""
ENCRYPTION_ENABLED = False

big_password = b"500 cigarettes"

def client_test():    
    sleep(1)
    
    connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER,
        encryption_enabled=True
    )
    
    connection.socket.connect(connection.address)
    
    establish_connection(connection, big_password)
    
    result = command_send_and_receive(connection, b"hello", b"3")
    
    print("[client] established?", result)#, result)



def server_test():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    
    connection = ConnectionObject(
        *server_socket.accept(), 
        type=ConnectionType.SERVER_TO_CLIENT,
        encryption_enabled=True
    ) 
    
    establish_connection(connection, big_password)
    command_receive_and_send(
        connection,
        PacketObject(b"helloo there!", PacketType.RESPONSE)
    )
    
    #print("[server] established?", connection.established)



if len(sys.argv) > 1:
    if sys.argv[1] == "client":
        client_test()
    elif sys.argv[1] == "server":
        Thread(target=server_test).start()
else:
    Thread(target=server_test).start()
    client_test()
"""
password = b"bytes"

def client_example():
    client_connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER,
        encryption_enabled=True
    )

    client_connection.socket.connect(
        client_connection.address
    )

    establish_connection(client_connection, password)

    client_procedures = SendReceiveProcedures(client_connection)

    # At this point it's up to on what you want to do.
    command_result_a = client_procedures.send_and_receive(
        PacketObject(b"hello", PacketType.COMMAND, id=b"\x03"),
        PacketType.RESPONSE
    )

    command_result_b = client_procedures.send_and_receive(
        PacketObject(b"hello", PacketType.COMMAND, id=b"\x03"),
        PacketType.RESPONSE
    )

    sleep(0.1) # sometimes the prints stack on each other.

    print("[client] command result a:", command_result_a)
    print("[client] command result b:", command_result_b)


# [Server Implementation]
def server_example():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)

    client_connection = ConnectionObject(
        *server_socket.accept(), 
        type=ConnectionType.SERVER_TO_CLIENT,
        encryption_enabled=True
    ) 
        
    establish_connection(client_connection, password)

    client_procedures = SendReceiveProcedures(client_connection)

    # At this point it's up to on what you want to do.

    # Function wrapping on receive.
    @client_procedures.receive_into_and_send(PacketType.COMMAND)
    def command(packet: PacketObject):
        print("[server] client command received", packet)
        
        if packet.payload.startswith(b"hello"):
            return PacketObject(b"world_a", PacketType.RESPONSE, packet.id)

    # Or send a premade packet upon receive.
    command_packet = client_procedures.receive_and_send(
        PacketObject(b"world_b", PacketType.RESPONSE),
        PacketType.COMMAND
    )
    
    print("[server] client command received", command_packet)

Thread(target=server_example).start()
sleep(1)
client_example()