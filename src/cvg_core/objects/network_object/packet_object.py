from enum import Enum
from dataclasses import dataclass, field


class PacketType(Enum):
    UNKNOWN = b"\xff"
    
    GATEWAY = b"\x00"
    EXCHANGE = b"\x01"
    
    CRYPTO = b"\xe0"
    
    PASSWORD = b"\x02"
    
    GRANTED = b"\xa0"
    DENIED = b"\xa1"
    
    COMMAND = b"\xc0"
    RESPONSE = b"\xc1"
    
    STREAM_START = b"\xb0"
    STREAM_DATA = b"\xb1"
    STREAM_END = b"\xb2"


@dataclass
class PacketObject:
    payload: bytes = field(default=b"")
    type: PacketType = field(default=PacketType.UNKNOWN)
    
    id: bytes = field(default=b"\x00")
    size: int = field(default=2)
    
    def __post_init__(self):
        if self.type is PacketType.UNKNOWN:
            # TODO replace ifs with asserts
            if len(self.payload) < 2:
                raise Exception("Invalid payload length!")
            
            self.id = self.payload[0:1]
            
            try:
                self.type = PacketType(self.payload[1:2])
            except:
                raise Exception("Invalid packet type!")
            
            self.payload = self.payload[2::]
        elif self.id is None:
            self.id = b"\x00"

        self.size = self.get_size()

    def to_bytes(self) -> bytes:
        return self.id + self.type.value + self.payload
    
    def get_size(self) -> int:    
        return len(self.to_bytes())
    
    def get_payload_size(self) -> int:
        return len(self.payload)

    def set_payload(self, data: bytes):
        self.payload = data
        self.size = self.get_size()
    
    def add_payload(self, data: bytes):
        self.payload += data
        self.size = self.get_size()
        
    def clear_payload(self):
        self.payload = b""
        self.size = 2
        
    