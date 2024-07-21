from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange

def __compare_password(password_packet: PacketObject, password: bytes):
    if password_packet.payload == password:
        return PacketObject(b"", PacketType.GRANTED)    
    else:
        return PacketObject(b"", PacketType.DENIED)


def __server_to_client(
    procedures: SendReceiveProcedures, password: bytes | None
):
    gateway_packet = procedures.receive_and_send(
        send_payload=b"",
        send_type=password and PacketType.PASSWORD or PacketType.GRANTED,
        receive_type=PacketType.GATEWAY
    )
    
    if password:
        password_result = procedures.receive_into_and_send(
            receive_type=PacketType.PASSWORD,
            receive_id=gateway_packet.id
        )(__compare_password, password)
        
        if password_result.type is PacketType.GRANTED:
            procedures.connection.established = True
        else:
            procedures.connection.established = False
        

def __client_to_server(
    procedures: SendReceiveProcedures, password: bytes | None
):
    access_check = procedures.send_and_receive(
        send_payload=b"",
        send_type=PacketType.GATEWAY
    )
    
    if access_check.type is PacketType.PASSWORD:
        password_check = procedures.send_and_receive(
            send_payload=password,
            send_type=PacketType.PASSWORD,
            send_id=access_check.id,
        )
        
        if password_check.type is PacketType.GRANTED:
            procedures.connection.established = True
        else:
            procedures.connection.established = False
            
    elif access_check.type is PacketType.GRANTED:
        procedures.connection.established = True
    else:
        procedures.connection.established = False
        # whut?


def establish_connection(
    connection: ConnectionObject, 
    password: bytes | None = None
) -> SendReceiveProcedures:
    crypto_exchange(connection)
    
    procedures = SendReceiveProcedures(connection)
    
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        __server_to_client(procedures, password)
    else:
        __client_to_server(procedures, password)
    
    return procedures