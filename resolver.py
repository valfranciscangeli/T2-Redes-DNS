import socket
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
def resolver(mensaje_consulta, original_id)-> DNS_message:
    
    print(f"enviando : \n {mensaje_consulta}")
    
    dns_root_answer = send_dns_message(
        raiz_DNS, puerto_DNS, mensaje_consulta, buff_size)
    
    print(f"Se recibio la primera respuesta: \n {dns_root_answer}")

    #dns_root_answer.id = original_id
    ans = dns_root_answer.Answer
    auth = dns_root_answer.Authority
    add = dns_root_answer.Additional

    # si la seccion answer NO viene vacía
    if ans != []:
        print(" la seccion answer no venia vacia")
        # if dns_root_answer.get_first_ip_in_answer_type_A != None:  # si hay un mensaje tipo A
        print("retornando la primera response")
        return dns_root_answer  # retorna un objeto DNS_message

    # hay NS en authority
    elif auth != []:
        posible_ns = dns_root_answer.get_first_ns_in_authority()
        if posible_ns != None:
            print("hay NS en authority ... ")
            if add != []:
                posible_ip = dns_root_answer.get_first_ip_in_additional_type_A()
                if posible_ip != None:
                    print("hay A en additional ... ")
                    ip = posible_ip._data
                    ip =  ".".join(map(str, ip))
                    print(f"ip: {ip} \n ===========================")
                    print("se encontró ip ...")
                    new_answer = send_dns_message(ip, puerto_DNS, mensaje_consulta, buff_size)
                    new_answer.id = original_id

                    print("retornando mensaje ...")
                    return new_answer  # retornamos el DNS_message resultante

            else:
                print(" no habia A en additional ... ")
                # primer name server que haya en authority
                name_server = dns_root_answer.get_first_ns_in_authority()
                if name_server != None:  # si se encontró un name server
                    # construimos una nueva consulta utilizando el name server encontrado
                    parsed_mensaje_consulta_og = parse_dns_message(
                        mensaje_consulta)
                    ANCOUNT = parsed_mensaje_consulta_og.ANCOUNT
                    NSCOUNT = parsed_mensaje_consulta_og.NSCOUNT
                    ARCOUNT = parsed_mensaje_consulta_og.ARCOUNT
                    Answer = parsed_mensaje_consulta_og.ANCOUNT
                    Authority = parsed_mensaje_consulta_og.Authority
                    Additional = parsed_mensaje_consulta_og.Additional

                    print("armando nueva consulta....")
                    nueva_consulta = DNS_message(original_id,
                                               name_server, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional)
                    #nueva_consulta = DNS_message(
                    #     original_id, name_server, 0, 0, 0)

                    print(f"consulta armada: \n {nueva_consulta}")

                    # Llamar recursivamente a resolver con la nueva consulta
                    print("llamada recursiva ...")
                    return resolver(nueva_consulta.build_binary_msg(), original_id)

    print("se va a retornar None")
    return None # type: ignore


# ======================================================
def my_resolver(port=8000):

    print('Creando socket - Recibir mensajes DNS')
    # socket no orientado a conexión
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    origin_address = ('localhost', port)

    # unimos el socket a la dirección address
    connection_socket.bind(origin_address)

    # nos quedamos esperando a que llegue un mensaje DNS
    print('esperamos mensajes ...')
    while True:
        # recibimos el mensaje usando recvfrom
        recv_message, origin_address = connection_socket.recvfrom(buff_size)

        parsed_original_msg = parse_dns_message(recv_message)
        original_id = parsed_original_msg.id

        msg_from_resolver = resolver(recv_message, original_id) # DNS_message
        print(f"se obtiene mensaje desde el resolver:\n {msg_from_resolver} \n")

        if msg_from_resolver != None:
            print("entramos a retornar el mensaje final ...")
            response = msg_from_resolver.build_dns_record().pack()
            final_send_dns_message(origin_address,response, buff_size)
            print(f"Mensaje enviado al cliente: \n {response}")
        else:
            print(f"No se pudo responder al cliente")

        # seguimos esperando por si llegan otras conexiones


my_resolver()  # ejectutamos el resolver
