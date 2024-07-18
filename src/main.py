from cvg_core.objects.crypto_object.ecdh_object import ECDHObject

alice_keys = ECDHObject()
bob_keys = ECDHObject()

alices_public_pem = alice_keys.to_public_pem()
bobs_public_pem = bob_keys.to_public_pem()

alices_aes_key = alice_keys.derive_aes_key(bobs_public_pem)
bobs_aes_key = bob_keys.derive_aes_key(alices_public_pem)


print(alices_aes_key == bobs_aes_key)