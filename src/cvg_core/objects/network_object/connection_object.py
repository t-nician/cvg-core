from enum import Enum
from dataclasses import dataclass, field

from socket import socket as _socket


from objects.crypto_object.ecdh_object import ECDHObject


class ConnectionState(Enum):
    GREETING = "greeting"
    AUTHORIZED = "authorized"
    RESPONDING = "responding"
    STREAMING = "streaming"


class ConnectionType(Enum):
    CLIENT_TO_SERVER = "client_to_server"
    SERVER_TO_CLIENT = "server_to_client"
    UNKNOWN = "unknown"


@dataclass
class ConnectionObject:
    socket: _socket = field(default=None)
    address: tuple[str, int] = field(default=("", -1))
    
    server_crypto: ECDHObject | None = field(default=None)
    client_crypto: ECDHObject | None = field(default=None)
    
    state: ConnectionState = field(default=ConnectionState.GREETING)
    type: ConnectionType = field(default=ConnectionType.UNKNOWN)
    
    def __post_init__(self):
        match type(self.type):
            case ConnectionType.CLIENT_TO_SERVER:
                self.client_crypto = ECDHObject()
            case ConnectionType.SERVER_TO_CLIENT:
                self.server_crypto = ECDHObject()
            case _:
                pass