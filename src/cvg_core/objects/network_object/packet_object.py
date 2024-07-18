from enum import Enum
from dataclasses import dataclass, field


class PacketType(Enum):
    UNKNOWN = b"\xff"
    
    GATEWAY = b"\x00"
    EXCHANGE = b"\x01"
    
    PASSWORD = b"\x02"
    
    COMMAND = b"\xc0"
    CRYPTO = b"\xc1"
    
    RESULT = b"\xc2"
    
    STREAM_START = b"\xb0"
    STREAM_DATA = b"\xb1"
    STREAM_END = b"\xb2"


@dataclass
class PacketObject:
    payload: bytes = field(default=b"")
    type: PacketType = field(default=PacketType.UNKNOWN)
    
    id: bytes = field(default=b"\x00")

    def __post_init__(self):
        if self.type is PacketType.UNKNOWN:
            if len(self.payload) < 2:
                raise "Invalid payload length!"
            
            self.id = self.payload[0:1]
            
            try:
                self.type = PacketType(self.payload[1:2])
            except:
                raise "Invalid packet type!"
            
            self.payload = self.payload[2::]

    def to_bytes(self) -> bytes:
        return self.id + self.type.value + self.payload

    