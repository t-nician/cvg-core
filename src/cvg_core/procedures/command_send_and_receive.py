from typing import Callable

from cvg_core.proper_procedures import SendReceiveProcedures

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

def command_send_and_receive(
    connection: ConnectionObject, 
    command: bytes,
    id: bytes | None = None
) -> PacketObject:
    return SendReceiveProcedures(connection).send_and_receive(
        PacketObject(command, PacketType.COMMAND, id),
        PacketType.RESPONSE
    )
    

def command_receive_and_send(
    connection: ConnectionObject,
    packet: PacketObject,
    id: bytes | None = None
) -> PacketObject:
    return SendReceiveProcedures(connection).receive_and_send(
        packet,
        PacketType.COMMAND,
        id
    )


def command_receive_into_and_send(
    connection: ConnectionObject,
    type: PacketType | None = None, 
    id: bytes | None = None
):
    procedures = SendReceiveProcedures(connection)
    
    def wrapper(func: Callable[[PacketObject], PacketObject], *args: any):
        packet = procedures.receive(id)
        result = func(packet, *args)
        
        if type:
            assert packet.type == type
        
        procedures.send(result)
        
        return result
    
    return wrapper