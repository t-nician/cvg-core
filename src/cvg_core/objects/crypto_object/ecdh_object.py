from enum import Enum
from typing import Callable
from dataclasses import dataclass, field

from Crypto.Cipher import AES

from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


@dataclass
class ECDHObject:
    public_key: None | bytes | ec.EllipticCurvePublicKey = field(
        default=None
    )
    
    private_key: None | bytes | ec.EllipticCurvePrivateKey = field(
        default=None
    )
    
    curve: ec.EllipticCurve = field(default_factory=ec.SECP521R1)
    backend: Callable = field(default_factory=default_backend)
    
    hkdf_length: int = field(default=32)
    hkdf_salt: bytes = field(default=b"")
    hkdf_info: bytes = field(default=b"")
    
    def __post_init__(self):
        _public_key_type = type(self.public_key)
        _private_key_type = type(self.private_key)

        if _public_key_type is bytes:
            self.public_key = serialization.load_pem_public_key(
                self.public_key
            )
        
        if self.public_key is None:
            if _private_key_type is bytes:
                self.private_key = serialization.load_pem_private_key(
                    self.private_key
                )
            elif self.private_key is None:
                self.private_key = ec.generate_private_key(
                    self.curve, self.backend
                )

                self.public_key = self.private_key.public_key()

    def to_public_pem(self) -> bytes:
        return self.public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def derive_secret(self, public_key: bytes | ec.EllipticCurve) -> bytes:
        if type(public_key) is bytes:
            public_key = serialization.load_pem_public_key(public_key)
        
        return self.private_key.exchange(
            ec.ECDH(), 
            public_key
        )
    
    def derive_aes_key(self, public_key: bytes | ec.EllipticCurve) -> bytes:    
        return HKDF(
            algorithm=hashes.SHA256(),
            length=self.hkdf_length,
            salt=self.hkdf_salt,
            info=self.hkdf_info,
            backend=self.backend
        ).derive(self.derive_secret(public_key))