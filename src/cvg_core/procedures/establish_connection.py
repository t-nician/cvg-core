from typing import Callable

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange


def __fab_granted(
    packet: PacketObject | bytes, 
    payload: bytes | None = b""
) -> PacketObject:
    if type(packet) is bytes:  
        return PacketObject(payload, PacketType.GRANTED, packet)
    else:
        return PacketObject(payload, PacketType.GRANTED, packet.id)


def __fab_denied(
    packet: PacketObject | bytes, 
    payload: bytes | None = b""
) -> PacketObject:
    if type(packet) is bytes:  
        return PacketObject(payload, PacketType.DENIED, packet)
    else:
        return PacketObject(payload, PacketType.DENIED, packet.id)


def __fab_password(
    packet: bytes | PacketObject,
    password: bytes | None = b""
):
    if type(packet) is bytes:  
        return PacketObject(password, PacketType.PASSWORD, packet)
    else:
        return PacketObject(password, PacketType.PASSWORD, packet.id)


def __exchange_password(
    packet: PacketObject, connection: ConnectionObject, 
    compare_password: bytes, procedures: SendReceiveProcedures
) -> PacketObject:
    received_password: PacketObject = procedures.send_and_receive(
        connection,
        __fab_password(packet)
    )

    if received_password.payload == compare_password:
        connection.established = True
        return __fab_granted(received_password)
    else:
        return __fab_denied(received_password)


def establish_connection(
    connection: ConnectionObject, 
    password: bytes | None = None
):  
    #f connection.encryption_enabled:
    crypto_exchange(connection)
    
    procedures = SendReceiveProcedures(connection)
      
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        gateway_packet: PacketObject
        
        if password:
            gateway_packet = procedures.receive_into_and_send(
                connection,
                PacketType.GATEWAY
            )(
                __exchange_password,
                connection,
                password,
                procedures
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
                __fab_password(entry_response, password)
            )
            
            if password_response.type is PacketType.GRANTED:
                connection.established = True
            else:
                raise Exception("Incorrect password!")
            
        elif entry_response.type is PacketType.GRANTED:
            connection.established = True