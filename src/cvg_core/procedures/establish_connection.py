from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

from cvg_core.proper_procedures import SendReceiveProcedures
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange

# NOTE remember to add connection.established value when done.

# password exchange plan
# client GATEWAY -> server
    # yes password:
        # server PASSWORD -> client
        # client PASSWORD -> server
        # server GRANTED/DENIED -> client
    # no password:
        # server GRANTED -> client

def __server_to_client(
    procedures: SendReceiveProcedures, password: bytes | None
):
    pass
    


def __client_to_server(
    procedures: SendReceiveProcedures, password: bytes | None
):
    pass


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

"""
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
    packet: PacketObject,
    compare_password: bytes, procedures: SendReceiveProcedures
) -> PacketObject:
    received_password: PacketObject = procedures.send_and_receive(
        __fab_password(packet)
    )

    if received_password.payload == compare_password:
        procedures.connection.established = True
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
                PacketType.GATEWAY
            )(
                __exchange_password,
                password,
                procedures
            )
        else:
            gateway_packet = procedures.receive_into_and_send(
                PacketType.GATEWAY
            )(__fab_granted)
        
        assert gateway_packet.type is PacketType.GRANTED
        
    elif connection.type is ConnectionType.CLIENT_TO_SERVER:
        entry_response: PacketObject = procedures.send_and_receive(
            PacketObject(b"", PacketType.GATEWAY)
        )
        
        if entry_response.type is PacketType.PASSWORD:            
            password_response: PacketObject = procedures.send_and_receive(
                __fab_password(entry_response, password)
            )
            
            if password_response.type is PacketType.GRANTED:
                connection.established = True
            else:
                raise Exception("Incorrect password!")
            
        elif entry_response.type is PacketType.GRANTED:
            connection.established = True"""