import sys

import cvg_core


if len(sys.argv) > 1:
    if sys.argv[1] == "test":
        cvg_core.tests.start_tests()

"""
from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM


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
    packet_result_a = client_procedures.send_and_receive(
        send_payload=b"hello", 
        send_type=PacketType.PACKET,
        send_id=b"\x03",
        receive_type=PacketType.PACKET
    )

    packet_result_b = client_procedures.send_and_receive(
        send_payload=b"hello", 
        send_type=PacketType.PACKET,
        send_id=b"\x03",
        receive_type=PacketType.PACKET
    )

    sleep(0.1) # sometimes the prints stack on each other.

    print("[client] packet result a:", packet_result_a)
    print("[client] packet result b:", packet_result_b)


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
    # ..._into_and_... always requires a PacketObject return inside the function.
    @client_procedures.receive_into_and_send(PacketType.PACKET)
    def packet(received_packet: PacketObject):
        print("[server] command received", received_packet)
        if received_packet.payload.startswith(b"hello"):
            return PacketObject(
                b"world_a", 
                PacketType.PACKET, 
                received_packet.id
            )

    # Or send a premade packet upon receive.
    received_packet = client_procedures.receive_and_send(
        send_payload=b"world_b", 
        send_type=PacketType.PACKET,
        receive_type=PacketType.PACKET
    )
    
    print("[server] client packet received", received_packet)


Thread(target=server_example).start()
sleep(1)
client_example()
"""