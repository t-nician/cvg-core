import sys

from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.establish_connection import establish_connection

from cvg_core.procedures.command_send_and_receive import command_send_and_receive, command_receive_and_send

ENCRYPTION_ENABLED = True

big_password = b"500 cigarettes"

def client_test():    
    sleep(1)
    
    connection = ConnectionObject(
        address=("127.0.0.1", 5000),
        socket=socket(AF_INET, SOCK_STREAM),
        type=ConnectionType.CLIENT_TO_SERVER,
        encryption_enabled=ENCRYPTION_ENABLED
    )
    
    connection.socket.connect(connection.address)
    
    establish_connection(connection, big_password)
    
    #result = command_send_and_receive(connection, b"hello")
    
    
    #sleep(0.1)
    
    #print(connection.established)
    
    #@send_and_receive(connection)
    #def test(packet: PacketObject):
    #    print("[client] [receive-into-and-send]", packet)
    #    return PacketObject(b"success", PacketType.RESPONSE)
    
    print("[client] established?", connection.established)#, result)



def server_test():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 5000))
    server_socket.listen(1)
    
    connection = ConnectionObject(
        *server_socket.accept(), 
        type=ConnectionType.SERVER_TO_CLIENT,
        encryption_enabled=ENCRYPTION_ENABLED
    ) 
    
    establish_connection(connection, big_password)
    #command_receive_and_send(
    #    connection,
    #    PacketObject(b"helloo there!", PacketType.RESPONSE)
    #)
    
    print("[server] established?", connection.established)



if len(sys.argv) > 1:
    if sys.argv[1] == "client":
        client_test()
    elif sys.argv[1] == "server":
        Thread(target=server_test).start()
else:
    Thread(target=server_test).start()
    client_test()
