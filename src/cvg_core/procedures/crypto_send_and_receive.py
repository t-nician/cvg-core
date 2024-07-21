import hashlib

from typing import Callable

from Crypto.Cipher import AES

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.objects.crypto_object.ecdh_object import ECDHObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive


def __derive_aes_key(connection: ConnectionObject):
    match connection.type:
        case ConnectionType.SERVER_TO_CLIENT:
            return connection.server_crypto.derive_aes_key(
                connection.client_crypto.public_key
            )
        case ConnectionType.CLIENT_TO_SERVER:
            return connection.client_crypto.derive_aes_key(
                connection.server_crypto.public_key
            )


def __to_public_pem(connection: ConnectionObject):
    match connection.type:
        case ConnectionType.SERVER_TO_CLIENT:
            return connection.server_crypto.to_public_pem()
        case ConnectionType.CLIENT_TO_SERVER:
            return connection.client_crypto.to_public_pem()


def decrypt_packet(
    connection: ConnectionObject, packet: PacketObject
) -> PacketObject:
    return PacketObject(
        AES.new(
            key=__derive_aes_key(connection),
            mode=AES.MODE_EAX,
            nonce=packet.payload[0:16]
        ).decrypt(packet.payload[16::])
    )


def encrypt_packet(
    connection: ConnectionObject, packet: PacketObject
) -> PacketObject:
    cipher = AES.new(
        key=__derive_aes_key(connection),
        mode=AES.MODE_EAX
    )
    
    return PacketObject(
        cipher.nonce + cipher.encrypt(packet.to_bytes()),
        PacketType.CRYPTO
    )


def crypto_exchange(connection: ConnectionObject):
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        if connection.encryption_enabled:
            client_pem = send_and_receive(
                connection,
                PacketObject(
                    __to_public_pem(connection),
                    PacketType.EXCHANGE
                ),
                PacketType.EXCHANGE
            )
        
            connection.client_crypto = ECDHObject(client_pem.payload)
            
            # TODO confirm crypto exchange. we just assume it's a success rn.
            crypto_send(
                connection, 
                PacketObject(b"Hello", PacketType.EXCHANGE, client_pem.id)
            )
        else:
            send(
                connection,
                PacketObject(b"Hello", PacketType.EXCHANGE)
            )
            
            connection.encryption_enabled = False
        
    else:
        server_exchange = receive(connection, PacketType.EXCHANGE)
        
        if server_exchange.payload.startswith(b"-----BEGIN PUBLIC KEY-----"):
            connection.client_crypto = ECDHObject()
            connection.server_crypto = ECDHObject(server_exchange.payload)
            
            send(
                connection,
                PacketObject(
                    __to_public_pem(connection), 
                    PacketType.EXCHANGE,
                    server_exchange.id
                )
            )
            
            # TODO confirm crypto exchange. we just assume it's a success rn.
            crypto_receive(connection, PacketType.EXCHANGE, server_exchange.id)
            
            connection.encryption_enabled = True
        elif server_exchange.payload == b"Hello":
            connection.encryption_enabled = False
        

def crypto_send(connection: ConnectionObject, packet: PacketObject):
    send(connection, encrypt_packet(connection, packet))
    

def crypto_receive(
    connection: ConnectionObject,
    receive_type: PacketType | None = None,
    id: None | bytes = None
) -> PacketObject | None:
    packet = receive(connection, PacketType.CRYPTO)
    
    result = decrypt_packet(connection, packet)
    
    if id:
        assert result.id == id
    
    if receive_type:
        # TODO move err msg, do not remove this. This assert is required.
        assert result.type is receive_type, f"got {result.type} expected {receive_type}"
    
    return result
        

def crypto_send_and_receive(
    connection: ConnectionObject,
    packet: PacketObject,
    receive_type: PacketType | None = None
) -> PacketObject | None:
    crypto_send(connection, packet)
    return crypto_receive(connection, receive_type, packet.id)


def crypto_receive_and_send(
    connection: ConnectionObject,
    send_packet: PacketObject,
    receive_type: PacketType | None = None,
    receive_id: bytes | None = None,
) -> PacketObject | None:
    result = crypto_receive(connection, receive_type, receive_id)

    send_packet.id = result.id
    
    crypto_send(connection, send_packet)
    
    return result


def crypto_receive_into_and_send(
    connection: ConnectionObject, 
    type: PacketType | None = None, 
    id: bytes | None = None
):
    def wrapper(func: Callable[[PacketObject], PacketObject], *args: any):
        packet = crypto_receive(connection, type, id)
        result = func(packet, *args)
        
        crypto_send(connection, result)
        
        return result
    
    return wrapper