import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib
from dns_message import *
from utils import *

from dnslib import DNSRecord, DNSQuestion, A, NS


# ======================================================
# variables globales:
puerto_DNS = 53
raiz_DNS = '192.33.4.12'
buff_size = 4096


# ======================================================
def resolver(mensaje_consulta, original_id):
    dns_root_answer = send_dns_message(
        raiz_DNS, puerto_DNS, mensaje_consulta, buff_size)

    dns_root_answer.id = original_id
    ans = dns_root_answer.Answer
    auth = dns_root_answer.Authority
    add = dns_root_answer.Additional

    # si la seccion answer NO viene vacía
    if ans != []:
        if find_type_msg_in_field(ans):  # si hay un mensaje tipo A
            return dns_root_answer  # retorna un objeto DNS_message

    # hay NS en authority
    elif auth != [] and find_type_msg_in_field(auth, NS):
        if add != [] and find_type_msg_in_field(add):  # hay A en additional
            ip = dns_root_answer.get_first_ip_in_additional()
            if ip != None:  # si se encontró una ip
                new_answer = send_dns_message(
                    ip, puerto_DNS, mensaje_consulta, buff_size)

                new_answer.id = original_id

                return new_answer  # retornamos el DNS_message resultante

        else:
            # primer name server que haya en authority
            name_server = dns_root_answer.get_first_ns_in_authority()
            if name_server != None:  # si se encontró un name server
                # construimos una nueva consulta utilizando el name server encontrado
                parsed_mensaje_consulta_og = parse_dns_message(
                    mensaje_consulta)
                ANCOUNT = parsed_mensaje_consulta_og.ANCOUNT
                NSCOUNT = parsed_mensaje_consulta_og.NSCOUNTCOUNT
                ARCOUNT = parsed_mensaje_consulta_og.ARCOUNT
                Answer = parsed_mensaje_consulta_og.ANCOUNT
                Authority = parsed_mensaje_consulta_og.Authority
                Additional = parsed_mensaje_consulta_og.Additional
                nueva_consulta = DNS_message(original_id,
                                             name_server, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional)
                # nueva_consulta = DNS_message(original_id, name_server, 0, 0)

                # Llamar recursivamente a resolver con la nueva consulta
                return resolver(nueva_consulta.build_binary_msg(), original_id)

    return None


# ======================================================
def my_resolver(port=8000):

    print('Creando socket - Recibir mensajes DNS')
    # socket no orientado a conexión
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    address = ('localhost', port)

    # unimos el socket a la dirección address
    connection_socket.bind(address)

    # nos quedamos esperando a que llegue un mensaje DNS
    print('esperamos mensajes ...')
    while True:
        # recibimos el mensaje usando recvfrom
        recv_message, address = connection_socket.recvfrom(buff_size)
        # parsed_message = parse_dns_message(recv_message)
        # print(f" -> Se ha recibido el siguiente mensaje: \n{parsed_message}")

        parsed_original_msg = parse_dns_message(recv_message)
        original_id = parsed_original_msg.id

        msg_from_resolver = resolver(recv_message, original_id)

        if msg_from_resolver != None:
            response = msg_from_resolver.build_binary_msg()
            send_dns_message(address, puerto_DNS, response, buff_size)
            print(f"Mensaje enviado al cliente: \n {response}")
        else:
            print(f"No se pudo responder al cliente")

        # seguimos esperando por si llegan otras conexiones

    connection_socket.close()  # si se sale del loop cerramos el socket


my_resolver()  # ejectutamos el resolver
