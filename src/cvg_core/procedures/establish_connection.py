from typing import Callable

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.procedures.send_and_receive import receive_into_and_send, receive_and_send, send_and_receive, send, receive
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange, crypto_receive_into_and_send, crypto_receive_and_send, crypto_send_and_receive, crypto_send, crypto_receive


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
    scope_send_and_receive: Callable[
        [ConnectionObject, PacketObject], PacketObject
    ],
    connection: ConnectionObject,
    packet: PacketObject, 
    compare_password: bytes
) -> PacketObject:
    received_password = scope_send_and_receive(
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
    scope_send_and_receive = send_and_receive
    #scope_send, scope_receive = send, receive
    
    #scope_receive_and_send = receive_and_send
    scope_receive_into_and_send = receive_into_and_send
    
    if connection.encryption_enabled:
        crypto_exchange(connection)
        
        scope_send_and_receive = crypto_send_and_receive
        #scope_send, scope_receive = crypto_send, crypto_receive
        
        #scope_receive_and_send = crypto_receive_and_send
        scope_receive_into_and_send = crypto_receive_into_and_send
    
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        gateway_packet: PacketObject
        
        if password:
            gateway_packet = scope_receive_into_and_send(
                connection,
                PacketType.GATEWAY
            )(
                lambda _: __exchange_password(
                    packet=_,
                    compare_password=password,
                    connection=connection,
                    scope_send_and_receive=scope_send_and_receive
                )
            )
        else:
            gateway_packet = scope_receive_into_and_send(
                connection,
                PacketType.GATEWAY
            )(__fab_granted)
        
        assert gateway_packet.type is PacketType.GRANTED
        
    elif connection.type is ConnectionType.CLIENT_TO_SERVER:
        entry_response: PacketObject = scope_send_and_receive(
            connection,
            PacketObject(b"", PacketType.GATEWAY)
        )
        
        if entry_response.type is PacketType.PASSWORD:            
            password_response: PacketObject = scope_send_and_receive(
                connection,
                __fab_password(entry_response.id, password)
            )
            
            if password_response.type is PacketType.GRANTED:
                connection.established = True
            else:
                raise Exception("Incorrect password!")
            
        elif entry_response.type is PacketType.GRANTED:
            connection.established = True