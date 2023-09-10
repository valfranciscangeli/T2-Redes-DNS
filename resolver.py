import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib
from dns_message import *


def my_resolver(port=8000, buff_size=4096):

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
        parsed_message = parse_dns_message(recv_message)
        print(f" -> Se ha recibido el siguiente mensaje: \n{parsed_message}")

        # seguimos esperando por si llegan otras conexiones

    connection_socket.close()  # si se sale del loop cerramos el socket

my_resolver()  # ejectutamos el resolver
