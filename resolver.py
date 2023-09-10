import socket
from dnslib.dns import CLASS, QTYPE
from dns_message import *
from dnslib import DNSRecord
# ======================================================
# configuracion de printeo
debug_mode = True
super_print_mode = False

# ======================================================
# variables globales:
puerto_DNS = 53
raiz_DNS = '192.33.4.12'
buff_size = 4096
root_address = (raiz_DNS, puerto_DNS)


# ======================================================
# recive mensaje en bytes y el id original
def resolver(mensaje_consulta, original_id, send_address=root_address, name_server = '.') -> DNS_message:

    if super_print_mode:
        print(f"enviando : \n {parse_dns_message(mensaje_consulta)}")
        
    parsed_mensaje_consulta = parse_dns_message(mensaje_consulta)

    if debug_mode:
        print(f"(debug) Consultando '{parsed_mensaje_consulta.Qname}' a '{name_server}' con dirección IP '{send_address[0]}'")
    dns_root_answer = send_dns_message(
        send_address, mensaje_consulta, buff_size, True)

    if super_print_mode:
        print(f"Se recibio una respuesta: \n {dns_root_answer}")

    if dns_root_answer != None:
        dns_root_answer.id = original_id
        ans = dns_root_answer.Answer
        auth = dns_root_answer.Authority
        add = dns_root_answer.Additional

        # si la seccion answer NO viene vacía
        if ans != []:
            if super_print_mode:
                print("la seccion answer no venia vacia ...")
            if dns_root_answer.get_first_ip_in_answer_type_A != None:  # si hay un mensaje tipo A
                if super_print_mode:    
                    print("retornando la respuesta ...")
                return dns_root_answer  # retorna un objeto DNS_message

        # hay NS en authority
        elif auth != []:
            if dns_root_answer.get_first_ns_in_authority() != None:
                if super_print_mode:
                    print("hay NS en authority ... ")
                if add != []:
                    first_RR__in_add = dns_root_answer.get_first_ip_in_additional_type_A()
                    if first_RR__in_add != None:
                        if super_print_mode:
                            print("hay A en additional ... ")
                        ip = first_RR__in_add[0]._data
                        ip =  ".".join(map(str, ip))
                        if super_print_mode:
                            print(f"ip: {ip} \n ===========================")
                            print("se encontró ip ...")
                        new_address = (ip, puerto_DNS)
                        if super_print_mode:
                            print(" llamada recursiva con nueva ip desde additional")
                            
                        nombre_de_dominio = first_RR__in_add[1]
                        return resolver(mensaje_consulta, original_id, new_address, nombre_de_dominio)

                else:
                    if super_print_mode:
                        print(" no habia A en additional ... ")
                    # primer name server que haya en authority
                    name_server = dns_root_answer.get_first_ns_in_authority()
                    if name_server != None:  # si se encontró un name server

                        # construimos una nueva consulta utilizando el name server encontrado
                        name_server_query = DNSRecord.question(name_server[0])
                        name_server_answer = resolver(
                            name_server_query.pack(), original_id)  # DNS_message
                        if name_server_answer != None:
                            # significa que obtuvimos un answer, hay que rescatar la ip
                            first_RR__in_ans = dns_root_answer.get_first_ip_in_answer_type_A()
                            if first_RR__in_ans != None:  # si hay un mensaje tipo A
                                name_server_ip = first_RR__in_ans
                                if super_print_mode:
                                    print(f"ip: {name_server_ip} \n ===========================")
                                    print("se encontró ip del name server ...")
                                new_address = (name_server_ip, puerto_DNS)
                                if super_print_mode:
                                    print("llamada recursiva con la direccion del nameserver")
                                return resolver(mensaje_consulta, original_id, new_address, name_server[1])

    if super_print_mode:
        print("no se pudo resolver, retornando None ...")
    return None  # type: ignore


# ======================================================
def my_resolver(port=8000):
    this_address = ('localhost', port)

    print('Creando socket - Recibir mensajes DNS ...')

    # socket no orientado a conexión
    connection_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # unimos el socket a la dirección address
    connection_socket.bind(this_address)

    # -----------------------------------------------------

    # nos quedamos esperando a que llegue un mensaje DNS
    print('esperando mensajes ...')
    contador_mensajes = 1
    while True:
        print(f"mensaje numero {contador_mensajes} ======================= \n")
        # recibimos el mensaje usando recvfrom
        recv_message, return_address = connection_socket.recvfrom(buff_size)
        if super_print_mode:
            print(f"direccion para retornar: {return_address}")

        parsed_recv_msg = parse_dns_message(recv_message)
        print("se recibió un mensaje ...")
        if super_print_mode:
            print(f"mensaje recibido: {parsed_recv_msg}")
        original_id = parsed_recv_msg.id

        # ----------------------------------------------------
        print("resolviendo query con resolver ....")

        msg_from_resolver = resolver(
            recv_message, original_id)  # recibe DNS_message
        if super_print_mode:
            print(f"se obtiene mensaje desde el resolver:\n {msg_from_resolver} \n")

        if msg_from_resolver != None:
            print("entramos a retornar el mensaje final ...")
            response = msg_from_resolver.build_bytes_msg()
            connection_socket.sendto(response, return_address)
            print("se envió un mensaje al cliente ...")
            if super_print_mode:
                print(f"Mensaje enviado al cliente: \n {parse_dns_message(response)}")
        else:
            print(f"No se pudo responder al cliente")
        

        # seguimos esperando por si llegan otras conexiones
        contador_mensajes +=1


my_resolver()  # ejectutamos el resolver
