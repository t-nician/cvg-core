from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

ERR_MSG_ID_MISMATCH = "PacketObject.id mismatch! Expected {0} got {0}"
ERR_MSG_STREAM_NOT_READY = "Connection is not ready for stream!"

def stream_receive(
    connection: ConnectionObject, size: int,
    id: bytes | None = b"\xff"
) -> PacketObject:
    compiled_payload = b""
    stream_packet = PacketObject(type=PacketType.STREAM_DATA, id=id)
    
    packet = send_and_receive(
        connection, 
        stream_packet
    )
    
    if packet.type is PacketType.STREAM_DATA:
        compiled_payload += packet.payload
    
    while True:
        packet = send_and_receive(connection, stream_packet)
        
        if packet.type is PacketType.STREAM_DATA:
            compiled_payload += packet.payload
        elif packet.type is PacketType.STREAM_END:
            break
    
    checksum = packet.payload
    # TODO handle failed checksumming also make it work :D
    final_message = send(
        connection,
        PacketObject(b"checksum_here", PacketType.STREAM_END, id=id)
    )
    #Aassert len(compiled_payload) + 2 == size, "PacketObject.size mismatch!"
    
    return PacketObject(compiled_payload)


def stream_send(connection: ConnectionObject, packet: PacketObject):
    raw_packet = packet.to_bytes()
    packet_size = packet.get_size()
    
    chunk_count = int(packet_size / 4094)
    chunk_remainder = packet_size % 4094
    
    chunk_list = [
        raw_packet[index : index + 4094] for index in range(
            0, 
            chunk_count,
            4094
        ) 
    ]
    
    chunk_list.append(raw_packet[packet_size - chunk_remainder: packet_size])
    
    #print("getting ready packet")
    ready_packet = send_and_receive(
        connection,
        PacketObject(
            packet_size.to_bytes(8, "big"), 
            PacketType.STREAM_START, 
            packet.id
        )
    )
    
    assert ready_packet.type is PacketType.STREAM_DATA
    
    for chunk in chunk_list:
        status_packet = send_and_receive(
            connection,
            PacketObject(chunk, PacketType.STREAM_DATA, packet.id)
        )
    
    # TODO message handling for when checksum fails.
    final_message = send_and_receive(
        connection,
        PacketObject(b"checksum-here", PacketType.STREAM_END, packet.id)
    )
    
    #print("[checksum]", checksum_packet)
    

def receive(
    connection: ConnectionObject, 
    id: bytes | None = None
) -> PacketObject | None:
    packet: PacketObject | None = None
    
    try:
        packet = PacketObject(connection.socket.recv(4096))
    except Exception as _:
        pass
    
    #print("[received]", packet)
    
    if packet and id is not None:
        assert packet.id == id, ERR_MSG_ID_MISMATCH.format(id, packet.id)
    
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
    connection: ConnectionObject, packet: PacketObject
) -> PacketObject:
    send(connection, packet)
    return receive(connection, packet.id)