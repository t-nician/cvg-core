from time import sleep
from typing import Callable

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject


def client_get(client: ConnectionObject, data: bytes) -> bytes:
    client.socket.send(data)
    return client.socket.recv(4096)


def create_client(host: str, port: int) -> ConnectionObject:
    return ConnectionObject(
        socket=socket(AF_INET, SOCK_STREAM),
        address=(host, port),
        type=ConnectionType.CLIENT_TO_SERVER
    )


def create_client_and_connect(host: str, port: int) -> SendReceiveProcedures:
    client = create_client(host, port)
    client.socket.connect(client.address)
    return client


def __server_client_connection(
    client: ConnectionObject, 
    callback: Callable[[ConnectionObject, bytes], bytes],
):
    while True:
        data = b""
        
        try:
            data = client.socket.recv(4096)
        except:
            break
        
        client.socket.send(
            callback(client, data)
        )


def __server_loop(
    server: socket,
    callback: Callable[[ConnectionObject, bytes], bytes],
    stop_after_one_connection: bool | None = False
    
):
    while True:
        Thread(
            target=__server_client_connection,
            args=(
                ConnectionObject(
                    *server.accept(),
                    type=ConnectionType.SERVER_TO_CLIENT
                ),
                callback
            )
        ).start()
        
        if stop_after_one_connection:
            break


def create_server(host: str, port: int, listeners: int | None = 1) -> socket:
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((host, port))
    server.listen(listeners)
    return server


def create_server_and_loop(
    host: str, port: int, 
    threaded: bool | None = False,
    stop_after_one_connection: bool | None = False
):
    def wrapper(callback: Callable[[bytes], bytes]):
        if threaded:
            Thread(
                target=__server_loop,
                args=(
                    create_server(host, port), 
                    callback, 
                    stop_after_one_connection
                )
            ).start()
            
            sleep(1)
        else:
            __server_loop(
                create_server(host, port), 
                callback, 
                stop_after_one_connection
            )
            
    return wrapper