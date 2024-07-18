from socket import socket, AF_INET, SOCK_STREAM

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionState, ConnectionObject

from cvg_core.objects.crypto_object.ecdh_object import ECDHObject

from cvg_core.procedures.send_and_receive import send_and_receive, send, receive


def client_test():
    pass


def server_test():
    pass


"""alice_keys = ECDHObject()
bob_keys = ECDHObject()

alices_public_pem = alice_keys.to_public_pem()
bobs_public_pem = bob_keys.to_public_pem()

alices_aes_key = alice_keys.derive_aes_key(bobs_public_pem)
bobs_aes_key = bob_keys.derive_aes_key(alices_public_pem)


print(alices_aes_key == bobs_aes_key)"""