from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive
from cvg_core.procedures.crypto_send_and_receive import crypto_exchange, crypto_send_and_receive, crypto_send, crypto_receive


def establish_connection(connection: ConnectionObject, password: bytes | None = None):
    scope_send_and_receive = send_and_receive
    scope_send, scope_receive = send, receive
    
    if connection.encryption_enabled:
        crypto_exchange(connection)
        
        scope_send_and_receive = crypto_send_and_receive
        scope_send, scope_receive = crypto_send, crypto_receive
    
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        gateway_packet: PacketObject = scope_receive(connection)
        
        assert gateway_packet.type is PacketType.GATEWAY
        
        if password:
            guessed_password = scope_send_and_receive(
                connection,
                PacketObject(b"", PacketType.PASSWORD, gateway_packet.id)
            )
            
            if guessed_password.payload == password:
                scope_send(
                    connection,
                    PacketObject(b"", PacketType.GRANTED, gateway_packet.id)
                )
                
                connection.established = True
            else:
                scope_send(
                    connection,
                    PacketObject(b"", PacketType.DENIED, gateway_packet.id)
                )
                
                raise Exception("Incorrect password!")

        else:
            scope_send(
                connection,
                PacketObject(b"", PacketType.GRANTED, gateway_packet.id)
            )
            
            connection.established = True
            
    elif connection.type is ConnectionType.CLIENT_TO_SERVER:
        entry_response: PacketObject = scope_send_and_receive(
            connection,
            PacketObject(b"", PacketType.GATEWAY)
        )
        
        if entry_response.type is PacketType.PASSWORD:            
            password_response: PacketObject = scope_send_and_receive(
                connection,
                PacketObject(password, PacketType.PASSWORD, entry_response.id)
            )
            
            assert password_response.type is PacketType.GRANTED, "Incorrect password!"
            
            connection.established = True
            
        elif entry_response.type is PacketType.GRANTED:
            connection.established = True