from typing import Callable

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange


def __fab_granted(
    id: int | PacketObject | None = None, 
    payload: bytes | None = b""
) -> PacketObject:
    if type(id) is PacketObject:
        id = id.id
        
    return PacketObject(payload, PacketType.GRANTED, id)


def __fab_denied(
    id: int | PacketObject | None = None, 
    payload: bytes | None = b""
) -> PacketObject:
    if type(id) is PacketObject:
        id = id.id
        
    return PacketObject(payload, PacketType.DENIED, id)


def __fab_password(
    id: int | PacketObject | None = None, 
    password: bytes | None = b""
):
    if type(id) is PacketObject:
        id = id.id
        
    return PacketObject(password, PacketType.PASSWORD, id)


def __exchange_password(
    procedures: SendReceiveProcedures,
    connection: ConnectionObject,
    packet: PacketObject, 
    compare_password: bytes
) -> PacketObject:
    received_password: PacketObject = procedures.send_and_receive(
        connection,
        __fab_password(packet)
    )

    if received_password.payload == compare_password:
        connection.established = True
        return __fab_granted(received_password.id)
    else:
        return __fab_denied(received_password.id)


def establish_connection(
    connection: ConnectionObject, 
    password: bytes | None = None
):  
    if connection.encryption_enabled:
        crypto_exchange(connection)
    
    procedures = SendReceiveProcedures(connection)
      
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        gateway_packet: PacketObject
        
        if password:
            gateway_packet = procedures.receive_into_and_send(
                connection,
                PacketType.GATEWAY
            )(
                lambda _: __exchange_password(
                    packet=_,
                    compare_password=password,
                    connection=connection,
                    procedures=procedures
                )
            )
        else:
            gateway_packet = procedures.receive_into_and_send(
                connection,
                PacketType.GATEWAY
            )(__fab_granted)
        
        assert gateway_packet.type is PacketType.GRANTED
        
    elif connection.type is ConnectionType.CLIENT_TO_SERVER:
        entry_response: PacketObject = procedures.send_and_receive(
            connection,
            PacketObject(b"", PacketType.GATEWAY)
        )
        
        if entry_response.type is PacketType.PASSWORD:            
            password_response: PacketObject = procedures.send_and_receive(
                connection,
                __fab_password(entry_response.id, password)
            )
            
            if password_response.type is PacketType.GRANTED:
                connection.established = True
            else:
                raise Exception("Incorrect password!")
            
        elif entry_response.type is PacketType.GRANTED:
            connection.established = True