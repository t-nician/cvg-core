from typing import Any, Callable
from dataclasses import dataclass, field

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionType, ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, receive_and_send, send, receive, receive_into_and_send
from cvg_core.procedures.crypto_send_and_receive import crypto_send_and_receive, crypto_receive_and_send, crypto_send, crypto_receive, crypto_receive_into_and_send


@dataclass
class SendReceiveProcedures:
    connection: ConnectionObject
    
    __receive_into_and_send: Callable[
        [ConnectionObject, PacketType | None, bytes | None],
        Callable
    ] = field(default=receive_into_and_send)
    
    __send_and_receive: Callable[
        [ConnectionObject, PacketObject, PacketType | None], PacketObject | None
    ] = field(default=send_and_receive)
    
    __receive_and_send: Callable[
        [ConnectionObject, PacketObject, PacketType | None, bytes | None], 
        PacketObject | None
    ] = field(default=receive_and_send)
    
    __receive: Callable[
        [ConnectionObject, bytes | None], PacketObject | None
    ] = field(default=receive)
    
    __send: Callable[
        [ConnectionObject, PacketObject], PacketObject | None
    ] = field(default=send)

    def __post_init__(self):
        if self.connection and self.connection.encryption_enabled:
            self.__receive_into_and_send = crypto_receive_into_and_send
            
            self.__send_and_receive = crypto_send_and_receive
            self.__receive_and_send = crypto_receive_and_send
            
            self.__receive = crypto_receive
            self.__send = crypto_send
    
    def receive_into_and_send(
        self, 
        receive_type: PacketType | None = None, 
        receive_id: bytes | None = None
    ) -> PacketObject:
        return self.__receive_into_and_send(
            self.connection,
            receive_type,
            receive_id
        )
    
    def send_and_receive(
        self,
        packet: PacketObject,
        receive_type: PacketType | None = None
    ) -> PacketObject:
        return self.__send_and_receive(
            self.connection,
            packet,
            receive_type,
        )
        
    def receive_and_send(
        self,
        send_packet: PacketObject,
        receive_type: PacketType | None = None,
        receive_id: bytes | None = None
    ) -> PacketObject:
        return self.__receive_and_send(
            self.connection,
            send_packet,
            receive_type,
            receive_id
        )
        
    def receive(
        self,
        receive_type: PacketType | None = None,
        receive_id: bytes | None = None
    ) -> PacketObject:
        return self.__receive(
            self.connection,
            receive_type,
            receive_id
        )
        
    def send(
        self,
        packet: PacketObject
    ):
        self.__send(self.connection, packet)