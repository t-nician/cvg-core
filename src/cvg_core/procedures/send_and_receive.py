from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

ERR_MSG_ID_MISMATCH = "PacketObject.id mismatch! Expected {0} got {0}"


def receive(
    connection: ConnectionObject, 
    id: bytes | None = None
) -> PacketObject | None:
    packet: PacketObject | None = None
    
    try:
        packet = PacketObject(connection.socket.recv(4096))
    except Exception as _:
        print(_)
    
    if packet and id is not None:
        assert packet.id == id, ERR_MSG_ID_MISMATCH.format(id, packet.id)
    
    return packet


def send(connection: ConnectionObject, packet: PacketObject):
    connection.socket.send(packet.to_bytes())


def stream_receive(
    connection: ConnectionObject, 
    id: bytes | None = None
) -> PacketObject:
    pass


def stream_send(connection: ConnectionObject, packet: PacketObject):
    encoded_packet = packet.to_bytes()
    
    packet_stream_iterations = int(encoded_packet / 4096)
    remaining_bytes_amount = encoded_packet % 4096
    
    
    
    #type(packet) is PacketObject and packet.to_bytes() or packet


def send_and_receive(
    connection: ConnectionObject, packet: PacketObject
) -> PacketObject:
    if packet.get_size() > 4096:
        stream_send(connection, packet)
    else:
        send(connection, packet)
    
    return receive(connection, packet.id)