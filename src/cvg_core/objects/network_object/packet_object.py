from enum import Enum
from dataclasses import dataclass, field


class PacketType(Enum):
    UNKNOWN = b"\xff"
    
    GATEWAY = b"\x00"
    EXCHANGE = b"\x01"
    
    PASSWORD = b"\x02"
    
    GRANTED = b"\xa0"
    DENIED = b"\xa1"
    
    COMMAND = b"\xc0"
    CRYPTO = b"\xc1"
    
    RESPONSE = b"\xc2"
    
    STREAM_START = b"\xb0"
    STREAM_DATA = b"\xb1"
    STREAM_END = b"\xb2"


@dataclass
class PacketObject:
    payload: bytes = field(default=b"")
    type: PacketType = field(default=PacketType.UNKNOWN)
    
    id: bytes = field(default=b"\x00")
    size: int = field(default=-1)
    
    def __post_init__(self):
        if self.type is PacketType.UNKNOWN:
            if len(self.payload) < 2:
                raise Exception("Invalid payload length!")
            
            self.id = self.payload[0:1]
            
            try:
                self.type = PacketType(self.payload[1:2])
            except:
                raise Exception("Invalid packet type!")
            
            self.payload = self.payload[2::]
            self.size = self.get_size()

    def to_bytes(self) -> bytes:
        encoded_packet = self.id + self.type.value + self.payload
        
        self.size = len(encoded_packet)
        
        return encoded_packet
    
    def get_size(self) -> int:
        if self.size <= 2:
            self.to_bytes()
            
        return self.size

    def set_payload(self, data: bytes):
        self.payload = data
        self.to_bytes()
    
    def add_payload(self, data: bytes):
        self.payload += data
        self.to_bytes()
        
    def clear_payload(self):
        self.payload = b""
        self.size = 2
        
    