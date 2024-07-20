import hashlib

from typing import Callable

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

ERR_MSG_ID_MISMATCH = "PacketObject.id mismatch! Expected {0} got {0}"
ERR_MSG_STREAM_NOT_READY = "Connection is not ready for stream!"

def stream_receive(
    connection: ConnectionObject, size: int,
    id: bytes | None = b"\xff"
) -> PacketObject:
    compiled_payload = b""
    stream_packet = PacketObject(b"", PacketType.STREAM_DATA, id)
    
    packet = send_and_receive(
        connection, 
        stream_packet
    )
    
    # TODO packet can return None handle interrupt
    
    if packet.type is PacketType.STREAM_DATA:
        compiled_payload += packet.payload
    
    while True:
        packet = send_and_receive(connection, stream_packet)
        
        # TODO packet can return None handle interrupt
        
        if packet.type is PacketType.STREAM_DATA:
            compiled_payload += packet.payload
        elif packet.type is PacketType.STREAM_END:
            break

    # TODO add err msg
    assert len(compiled_payload) == size

    md5_sum = hashlib.md5()
    md5_sum.update(compiled_payload)
    
    received_checksum = packet.payload
    checksum = md5_sum.digest()
    
    send(
        connection,
        PacketObject(checksum, PacketType.STREAM_END)
    )
    
    assert checksum == received_checksum, "Receive stream checksum failed!"
    
    return PacketObject(compiled_payload)


def stream_send(connection: ConnectionObject, packet: PacketObject):
    raw_packet = packet.to_bytes()
    packet_size = packet.get_size()
    
    chunk_count = int(packet_size / 4094)
    chunk_remainder = packet_size % 4094
    
    chunk_list = [
        raw_packet[index : index + 4094] for index in range(
            0, 
            chunk_count * 4094,
            4094
        ) 
    ]
    
    chunk_list.append(raw_packet[packet_size - chunk_remainder: packet_size])
    
    ready_packet = send_and_receive(
        connection,
        PacketObject(
            packet_size.to_bytes(8, "big"), 
            PacketType.STREAM_START, 
            packet.id
        ),
        PacketType.STREAM_DATA
    )
    
    # TODO packet can return None handle interrupt
    
    for chunk in chunk_list:
        status_packet = send_and_receive(
            connection,
            PacketObject(chunk, PacketType.STREAM_DATA, packet.id)
        )
        
        # TODO stream interrupt, status_packet can return None!
        # TODO check if status is not stream_data, could be cancelled/failed.
        
    # TODO is this really the cleanest I can do?
    md5_sum = hashlib.md5()
    md5_sum.update(raw_packet)
    
    checksum = md5_sum.digest()

    received_checksum = send_and_receive(
        connection,
        PacketObject(
            checksum, 
            PacketType.STREAM_END, 
            packet.id
        )
    ).payload
    
    # TODO move err msg
    assert checksum == received_checksum, "Send stream checksum failed!"
    

def receive(
    connection: ConnectionObject, 
    receive_type: PacketType | None = None,
    id: bytes | None = None
) -> PacketObject | None:
    packet: PacketObject | None = None
    
    try:
        packet = PacketObject(connection.socket.recv(4096))
    except Exception as _:
        pass
    
    if packet and id is not None:
        assert packet.id == id, ERR_MSG_ID_MISMATCH.format(id, packet.id)
    
    # TODO move err msg
    if packet and receive_type:
        assert packet.type is receive_type, f"expected {receive_type} got {packet.type}"
    
    if packet is not None and packet.type is PacketType.STREAM_START:
        packet = stream_receive(
            connection,
            int.from_bytes(packet.payload, "big"),
            packet.id
        )
    
    return packet


def send(connection: ConnectionObject, packet: PacketObject):
    if packet.get_size() > 4096:
        stream_send(connection, packet)
    else:
        connection.socket.send(packet.to_bytes())


def send_and_receive(
    connection: ConnectionObject, packet: PacketObject,
    receive_type: PacketType | None = None
) -> PacketObject | None:
    send(connection, packet)
    
    result = receive(connection, receive_type, packet.id)
    
    if receive_type:
        # TODO add err msg.
        assert result.type is receive_type
    
    return result


def receive_and_send(
    connection: ConnectionObject,
    send_packet: PacketObject,
    receive_type: PacketType | None = None,
    id: bytes | None = None
) -> PacketObject | None:
    result = receive(connection, receive_type, id)

    send(connection, send_packet)
    
    return result


def receive_into_and_send(
    connection: ConnectionObject, 
    type: PacketType | None = None, 
    id: bytes | None = None
):
    def wrapper(func: Callable[[PacketObject], PacketObject], *args: any):
        packet = receive(connection, type, id)
        result = func(packet, *args)
        
        send(connection, result)
        
        return result
    
    return wrapper