import socket
from dnslib.dns import CLASS, QTYPE
from dns_message import *
from utils import *
from dnslib import DNSRecord


# ======================================================
# variables globales:
puerto_DNS = 53
raiz_DNS = '192.33.4.12'
buff_size = 4096
root_address = (raiz_DNS, puerto_DNS)


# ======================================================
# recive mensaje en bytes y el id original
def resolver(mensaje_consulta, original_id, send_address=root_address) -> DNS_message:

    print(f"enviando : \n {parse_dns_message(mensaje_consulta)}")

    dns_root_answer = send_dns_message(
        send_address, mensaje_consulta, buff_size, True)

    print(f"Se recibio una respuesta: \n {dns_root_answer}")

    if dns_root_answer != None:
        dns_root_answer.id = original_id
        ans = dns_root_answer.Answer
        auth = dns_root_answer.Authority
        add = dns_root_answer.Additional

        # si la seccion answer NO viene vacía
        if ans != []:
            print("la seccion answer no venia vacia ...")
            if dns_root_answer.get_first_ip_in_answer_type_A != None:  # si hay un mensaje tipo A
                print("retornando la respuesta ...")
                return dns_root_answer  # retorna un objeto DNS_message

        # hay NS en authority
        elif auth != []:
            if dns_root_answer.get_first_ns_in_authority() != None:
                print("hay NS en authority ... ")
                if add != []:
                    posible_ip = dns_root_answer.get_first_ip_in_additional_type_A()
                    if posible_ip != None:
                        print("hay A en additional ... ")
                        ip = posible_ip._data
                        ip =  ".".join(map(str, ip))
                        print(f"ip: {ip} \n ===========================")
                        print("se encontró ip ...")
                        new_address = (ip, puerto_DNS)
                        print(" llamada recursiva con nueva ip desde additional")
                        return resolver(mensaje_consulta, original_id, new_address)

                else:
                    print(" no habia A en additional ... ")
                    # primer name server que haya en authority
                    name_server = dns_root_answer.get_first_ns_in_authority()
                    if name_server != None:  # si se encontró un name server

                        # construimos una nueva consulta utilizando el name server encontrado
                        name_server_query = DNSRecord.question(name_server)
                        name_server_answer = resolver(
                            name_server_query.pack(), original_id)  # DNS_message
                        if name_server_answer != None:
                            # significa que obtuvimos un answer, hay que rescatar la ip
                            posible_ip = dns_root_answer.get_first_ip_in_answer_type_A()
                            if posible_ip != None:  # si hay un mensaje tipo A
                                name_server_ip = posible_ip
                                print(f"ip: {name_server_ip} \n ===========================")
                                print("se encontró ip del name server ...")
                                new_address = (name_server_ip, puerto_DNS)
                                print("llamada recursiva con la direccion del nameserver")
                                return resolver(mensaje_consulta, original_id, new_address)

    print("no se pudo resolver, retornando None ...")
    return None  # type: ignore


# ======================================================
def my_resolver(port=8000):
    this_address = ('localhost', port)

    print('Creando socket - Recibir mensajes DNS')

    # socket no orientado a conexión
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # unimos el socket a la dirección address
    connection_socket.bind(this_address)

    # -----------------------------------------------------

    # nos quedamos esperando a que llegue un mensaje DNS
    print('esperamos mensajes ...')
    contador_mensajes = 1
    while True:
        print(f"mensaje numero {contador_mensajes} ======================= \n")
        # recibimos el mensaje usando recvfrom
        recv_message, return_address = connection_socket.recvfrom(buff_size)
        print(f"direccion para retornar: {return_address}")

        parsed_recv_msg = parse_dns_message(recv_message)
        print(f"mensaje recibido: {parsed_recv_msg}")
        original_id = parsed_recv_msg.id

        # ----------------------------------------------------
        print("resolviendo query con resolver ....")

        msg_from_resolver = resolver(
            recv_message, original_id)  # recibe DNS_message
        print(
            f"se obtiene mensaje desde el resolver:\n {msg_from_resolver} \n")

        if msg_from_resolver != None:
            print("entramos a retornar el mensaje final ...")
            response = msg_from_resolver.build_bytes_msg()
            connection_socket.sendto(response, return_address)
            print(f"Mensaje enviado al cliente: \n {parse_dns_message(response)}")
        else:
            print(f"No se pudo responder al cliente")
        

        # seguimos esperando por si llegan otras conexiones
        contador_mensajes +=1


my_resolver()  # ejectutamos el resolver
