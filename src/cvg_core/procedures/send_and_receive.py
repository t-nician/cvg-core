from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

def stream_receive(connection: ConnectionObject) -> PacketObject:
    pass


def stream_send(connection: ConnectionObject):
    pass


def receive(connection: ConnectionObject) -> PacketObject:
    pass


def send(connection: ConnectionObject):
    pass


def send_and_receive(connection: ConnectionObject) -> PacketObject:
    pass