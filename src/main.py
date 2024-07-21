#pip install cvg-core

import sys

from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core import SendReceiveProcedures, PacketType, ConnectionType, PacketObject, ConnectionObject, establish_connection

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

    client_procedures = establish_connection(client_connection, password)

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
        
    client_procedures = establish_connection(client_connection, password)

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