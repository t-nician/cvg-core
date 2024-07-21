## Client - Vault - Guard: Core
This is the core tooling for a network/data sharing protocol. \
Main functionality is for wrapping a socket.

----

* It can encrypt a socket connection with [ECDH-SECP521R1 -> AES256.](https://github.com/t-nician/cvg-core/blob/main/src/cvg_core/objects/crypto_object/ecdh_object.py)

    * If the server has encryption enabled but the client doesn't it will- \
Force the client to enable encryption before continuing the connection.

    * If the server has encryption disabled and the client does it will- \
Force the client to disable encryption before continuing the connection \
<sup> I'm probably not going to leave this as a 'feature' for obvious reasons </sup>

---
* [You can add a password/key to the server the client requires to get authorized.](https://github.com/t-nician/cvg-core/blob/main/src/cvg_core/procedures/establish_connection.py#L40) \
<sup> NOTE: If the server has encryption enabled, it will only do key exchange after encryption has been established </sup>


## How do you use it?
Here are some brief examples on establishing a connection using cvg-core.
```python
from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.establish_connection import establish_connection

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

# [Shared]
password = None # or b"bytes"

# [Client Implementation]
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
```