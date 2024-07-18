from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive


def client_test():    
    connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER
    )
    
    sleep(2)
    
    connection.socket.connect(connection.address)
    
    send(
        connection, 
        PacketObject(b"Hello from client!", PacketType.GATEWAY, id=b"a")
    )
    
    sleep(0.1)
    
    print("[client received]", receive(connection, id=b"b"))


def server_test():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    
    connection = ConnectionObject(*server_socket.accept())
    packet = receive(connection)
    
    print(f"[server received] {connection.address}:", packet)
    
    send(connection, PacketObject(b"Hello!", PacketType.GRANTED, packet.id))

Thread(target=server_test).start()
client_test()

"""alice_keys = ECDHObject()
bob_keys = ECDHObject()

alices_public_pem = alice_keys.to_public_pem()
bobs_public_pem = bob_keys.to_public_pem()

alices_aes_key = alice_keys.derive_aes_key(bobs_public_pem)
bobs_aes_key = bob_keys.derive_aes_key(alices_public_pem)


print(alices_aes_key == bobs_aes_key)"""