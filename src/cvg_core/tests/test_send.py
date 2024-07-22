from time import sleep
from threading import Thread

from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.proper_procedures import SendReceiveProcedures

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

from cvg_core.tests.shortcut import create_client_and_connect, create_server_and_accept, print_and_save

print = print_and_save

SERVER_HOST, SERVER_PORT = "127.0.0.1", 5000

TEST_A_PACKET = PacketObject(b"test_a", PacketType.PACKET, id=b"\x9e")
TEST_A_ENCODED_PACKET = TEST_A_PACKET.to_bytes()

SPLIT_LINE = "-" * 30

def test_server():
    procedures = create_server_and_accept(SERVER_HOST, SERVER_PORT)
    


def test_client():
    procedures = create_client_and_connect(SERVER_HOST, SERVER_PORT)    

    sleep(0.1)
    
    return "success!"

def start_tests():
    print("running test_server()...\nrunning test_client()...\n" + SPLIT_LINE)
    
    Thread(target=test_server).start()
    
    sleep(1)
    
    return test_client()