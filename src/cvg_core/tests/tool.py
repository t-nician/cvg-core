from time import sleep
from typing import Callable
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM
from dataclasses import dataclass, field

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


def create_server(host: str, port: int, listeners: int | None = 1) -> socket:
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((host, port))
    server.listen(listeners)
    return server


@dataclass
class ToolServer:
    host: str = field(default="127.0.0.1")
    port: int = field(default=5000)
    
    listeners: int = field(default=1)
    
    threaded: bool = field(default=True)
    
    start_on_create: bool = field(default=False)
    stop_after_one_connection: bool = field(default=True)
    
    __on_data: Callable[[ConnectionObject, bytes], bytes] = field(
        default=lambda _, __: ( b"" )
    )
    
    __socket: socket = field(default=None)
    
    def __post_init__(self):
        self.__socket = socket(AF_INET, SOCK_STREAM)
        self.__socket.bind((self.host, self.port))
        self.__socket.listen(self.listeners)
        
        if self.start_on_create:
            self.start()
    
    def __client_connection(self, client_connection: ConnectionObject):
        while True:
            data = b""
            
            try:
                data = client_connection.socket.recv(4096)
            except:
                break
            
            client_connection.socket.send(
                self.__on_data(client_connection, data)
            )
    
    def __server_loop(self):
        while True:
            client_connection = ConnectionObject(
                *self.__socket.accept(),
                type=ConnectionType.SERVER_TO_CLIENT
            )
            
            if self.threaded:
                Thread(
                    target=self.__client_connection, 
                    args=(client_connection,)
                ).start()
            else:
                self.__client_connection(client_connection)
                
                if self.stop_after_one_connection:
                    break
    
    def start(self, on_data: Callable[[ConnectionObject, bytes], bytes]):
        if self.threaded and self.stop_after_one_connection:
            raise Exception(
                "Cannot be threaded and stop after one connection..."
            )
        
        self.__on_data = on_data
        
        if self.threaded:
            Thread(target=self.__server_loop).start()
        else:
            self.__server_loop()
            

@dataclass
class ToolClient:
    connection: ConnectionObject = field(default_factory=ConnectionObject)
    
    def __post_init__(self):
        self.connection.type = ConnectionType.CLIENT_TO_SERVER
        self.connection.address = ("127.0.0.1", 5000)
        
    def connect(self):
        self.connection.socket.connect(self.connection.address)
    
    def receive(self):
        try:
            return self.connection.socket.recv(4096)
        except:
            return None
    
    def send(self, data: bytes):
        self.connection.socket.send(data)
    
    def post(self, data: bytes):
        self.send(data)
    
    def get(self, data: bytes) -> bytes:
        self.send(data)
        return self.receive()