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
        
        cipher = AES.new(
            key=__derive_aes_key(connection),
            mode=AES.MODE_EAX
        )
        
        crypto_confirm = send(
            connection,
            PacketObject(
                cipher.nonce + cipher.encrypt(b"Hello!"),
                PacketType.EXCHANGE
            )
        )
        
    else:
        server_pem = receive(connection)
        
        assert server_pem.type is PacketType.EXCHANGE
        
        connection.server_crypto = ECDHObject(server_pem.payload)
        
        crypto_test = send_and_receive(
            connection,
            PacketObject(
                __to_public_pem(connection), 
                PacketType.EXCHANGE,
                server_pem.id
            )
        )
        
        cipher = AES.new(
            key=__derive_aes_key(connection),
            mode=AES.MODE_EAX,
            nonce=crypto_test.payload[0:16]
        )
        
        print("[decrypt]", cipher.decrypt(crypto_test.payload[16::]))


def crypto_send(connection: ConnectionObject, packet: PacketObject):
    encryption_key = __derive_aes_key(connection)
    
    cipher = AES.new(key=encryption_key, mode=AES.MODE_EAX)
    
    nonce = cipher.nonce
    raw_encrypted_packet = cipher.encrypt(packet.to_bytes())
    
    crypto_packet = PacketObject(
        nonce + raw_encrypted_packet,
        PacketType.CRYPTO,
        id=packet.id
    )
    
    send(connection, crypto_packet)


def crypto_receive(connection: ConnectionObject, id: None | bytes = None):
    packet = receive(connection, id=id)
    
    if packet.type is PacketType.CRYPTO:
        encryption_key = __derive_aes_key(connection)
        
        