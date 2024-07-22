from time import sleep
from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.proper_procedures import SendReceiveProcedures

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

def create_server_and_accept(
    host: str, port: int,
    encryption: bool | None = False
) -> SendReceiveProcedures:
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    procedures = SendReceiveProcedures(
        ConnectionObject(
            *server_socket.accept(),
            type=ConnectionType.SERVER_TO_CLIENT,
            encryption_enabled=encryption
        )
    )
    
    sleep(0.1)
    
    print(f"server({host}:{port}) connected client{procedures.connection.address}")
    
    return procedures


def create_client_and_connect(
    host: str, port: int,
    encryption: bool | None = False
) -> SendReceiveProcedures:
    procedures = SendReceiveProcedures(
        ConnectionObject(
            address=(host, port),
            type=ConnectionType.CLIENT_TO_SERVER,
            encryption_enabled=encryption
        )
    )
    
    procedures.connection.socket.connect(
        procedures.connection.address
    )
    
    print(f"client{procedures.connection.socket.getsockname()} connected server{procedures.connection.address}")
    
    return procedures


def print_and_save(*args: any):
    print(*args)
    
    with open("log.txt", "a") as file:
        file.write(' '.join(args) + "\n")