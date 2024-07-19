import hashlib

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
        PacketType.CRYPTO,
        id=packet.id
    )


def crypto_exchange(connection: ConnectionObject):
    if connection.type is ConnectionType.SERVER_TO_CLIENT:
        client_pem = send_and_receive(
            connection,
            PacketObject(
                __to_public_pem(connection),
                PacketType.EXCHANGE
            )
        )
        
        assert client_pem.type is PacketType.EXCHANGE
        
        connection.client_crypto = ECDHObject(client_pem.payload)
        
        # TODO confirm crypto exchange. we just assume it's a success rn.
        crypto_send(connection, PacketObject(b"Hello", PacketType.EXCHANGE))
        
    else:
        server_pem = receive(connection)
        
        assert server_pem.type is PacketType.EXCHANGE
        
        connection.server_crypto = ECDHObject(server_pem.payload)
        
        send(
            connection,
            PacketObject(
                __to_public_pem(connection), 
                PacketType.EXCHANGE,
                server_pem.id
            )
        )
        
        # TODO confirm crypto exchange. we just assume it's a success rn.
        crypto_receive(connection)
        
        connection.encryption_enabled = True
        

def crypto_send(connection: ConnectionObject, packet: PacketObject):
    send(connection, encrypt_packet(connection, packet))
    

def crypto_receive(
    connection: ConnectionObject, 
    id: None | bytes = None
) -> PacketObject | None:
    packet = receive(connection, id=id)
    
    assert packet.type is PacketType.CRYPTO
    
    return decrypt_packet(connection, packet)
        

def crypto_send_and_receive(
    connection: ConnectionObject,
    packet: PacketObject
) -> PacketObject | None:
    crypto_send(connection, packet)
    return crypto_receive(connection, packet.id)