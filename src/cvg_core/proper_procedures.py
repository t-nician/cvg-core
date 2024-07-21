from typing import Callable
from dataclasses import dataclass, field

from cvg_core.objects.network_object.packet_object import PacketType, PacketObject
from cvg_core.objects.network_object.connection_object import ConnectionObject

from cvg_core.procedures.send_and_receive import send_and_receive, receive_and_send, send, receive, receive_into_and_send
from cvg_core.procedures.crypto_send_and_receive import crypto_send_and_receive, crypto_receive_and_send, crypto_send, crypto_receive, crypto_receive_into_and_send


@dataclass
class SendReceiveProcedures:
    connection: ConnectionObject
    
    __receive_into_and_send: Callable = field(default=receive_into_and_send)
    
    __send_and_receive: Callable = field(default=send_and_receive)
    __receive_and_send: Callable = field(default=receive_and_send)
    
    __receive: Callable = field(default=receive)
    __send: Callable = field(default=send)

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
    ):
        def wrapper(func, *args: any) -> PacketObject:
            return self.__receive_into_and_send(
                self.connection,
                receive_type,
                receive_id
            )(func, *args)
        return wrapper
    
    def send_and_receive(
        self,
        send_payload: bytes,
        send_type: PacketType,
        send_id: bytes | None = None,
        
        receive_type: PacketType | None = None
    ) -> PacketObject:
        return self.__send_and_receive(
            self.connection,
            PacketObject(send_payload, send_type, send_id),
            receive_type,
        )
        
    def receive_and_send(
        self,
        send_payload: bytes,
        send_type: PacketType,
        
        receive_type: PacketType | None = None,
        receive_id: bytes | None = None
    ) -> PacketObject:
        return self.__receive_and_send(
            self.connection,
            PacketObject(send_payload, send_type, receive_id),
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
        send_payload: bytes,
        send_type: PacketType,
        send_id: bytes | None = None
    ):
        self.__send(
            self.connection, 
            PacketObject(send_payload, send_type, send_id)
        )