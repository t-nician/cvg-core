from typing import Callable
from dataclasses import dataclass, field

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, receive_and_send, send, receive, receive_into_and_send
from cvg_core.procedures.crypto_send_and_receive import crypto_send_and_receive, crypto_receive_and_send, crypto_send, crypto_receive, crypto_receive_into_and_send


@dataclass
class SendReceiveProcedures:
    connection: ConnectionObject
    
    receive_into_and_send: Callable[
        [ConnectionObject, PacketType | None, bytes | None],
        Callable
    ] = field(default=receive_into_and_send)
    
    send_and_receive: Callable[
        [ConnectionObject, PacketObject, PacketType | None], PacketObject | None
    ] = field(default=send_and_receive)
    
    receive_and_send: Callable[
        [ConnectionObject, PacketObject, PacketType | None, bytes | None], 
        PacketObject | None
    ] = field(default=receive_and_send)
    
    receive: Callable[
        [ConnectionObject, bytes | None], PacketObject | None
    ] = field(default=receive)
    
    send: Callable[
        [ConnectionObject, PacketObject], PacketObject | None
    ] = field(default=send)
    
    def __post_init__(self):
        if self.connection and self.connection.encryption_enabled:
            self.receive_into_and_send = crypto_receive_into_and_send
            
            self.send_and_receive = crypto_send_and_receive
            self.receive_and_send = crypto_receive_and_send
            
            self.receive = crypto_receive
            self.send = crypto_send
            