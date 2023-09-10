import socket
from dns_message import *
from dnslib import DNSRecord, DNSQuestion, A, NS

def final_send_dns_message(address, question_message, buffer_size):
    server_address = address
    # no orientado a conexion
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(question_message, server_address)
        # En data quedará la respuesta a nuestra consulta
        print("se envió la respuesta")
    finally:
        print("chaoooo...")
        sock.close()

# ===========================================================
def send_dns_message(address, port, question_message, buffer_size):
    server_address = (address, port)
    # no orientado a conexion
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(question_message, server_address)
        # En data quedará la respuesta a nuestra consulta
        data, _ = sock.recvfrom(buffer_size)
        # le pedimos a dnslib que haga el trabajo de parsing por nosotros
        d = parse_dns_message(data)
    finally:
        sock.close()
    # Ojo que los datos de la respuesta van en en una estructura de datos
    return d

# ===========================================================


def find_type_msg_in_field(full_field, tipo_de_consulta):

    for rr in full_field:
        if isinstance(rr, tipo_de_consulta):
            return True

    return False
