import socket
from dns_message import *


# retorna DNS_message o None
def send_dns_message(address, message_in_bytes, buffer_size:int, wait_for_response:bool):
    # no orientado a conexion
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    response = None
    try:
        print(f"enviando mensaje a {address} ...")
        sock.sendto(message_in_bytes, address)
        print("mensaje enviado ...")
        if wait_for_response:
            print("recibiendo respuesta ...")
            data, _ = sock.recvfrom(buffer_size)
            print("parseando respuesta ...")
            response = parse_dns_message(data)
    finally:
        print("cerrando conexión ...")
        sock.close()
        print("conexión cerrada ...")
        
    return response