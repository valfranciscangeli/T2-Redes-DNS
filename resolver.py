import socket
from dnslib.dns import CLASS, QTYPE
from dns_message import *
from dnslib import DNSRecord
from cache import *
# ======================================================
# configuracion de printeo
debug_mode = True

# ======================================================
# variables globales:
puerto_DNS = 53
raiz_DNS = '192.33.4.12'
buff_size = 4096
root_address = (raiz_DNS, puerto_DNS)
nombre_archivo_cache = "resolver_cache.txt"
global registros_cache
registros_cache = []


# ======================================================
# recive mensaje en bytes y el id original
def resolver(mensaje_consulta, original_id, send_address=root_address, name_server='.') -> DNS_message:

    parsed_mensaje_consulta = parse_dns_message(mensaje_consulta)
    
    # buscamos en cache: ================
    dominio_buscado = parsed_mensaje_consulta.Qname
    print("buscando ip en cache")
    ip_buscada = buscar_ip_por_nombre(registros_cache, dominio_buscado)
    if ip_buscada !=None:
        print("se encontro ip en cache, actualizando registros ...")
        actualizar_registros(registros_cache, dominio_buscado, ip_buscada)
        
        print(f"creando respuesta con lo encontrado en cache: {ip_buscada}")
        ip_answer = create_answer_message(dominio_buscado, ip_buscada, original_id, parsed_mensaje_consulta.build_dns_record())
        if debug_mode:
            print(f"(debug) Cache: Retornando '{dominio_buscado}'en '{ip_buscada}'")
    
        return parse_dns_record(ip_answer)
    
    else:
        # no estaba en cache: ================
        print("la direccion no estaba en caché ...")
        if debug_mode:
            print(
                f"(debug) Consultando '{parsed_mensaje_consulta.Qname}' a '{name_server}' con dirección IP '{send_address[0]}'")
        dns_root_answer = send_dns_message(send_address, mensaje_consulta, buff_size, True)

        if dns_root_answer != None:
            dns_root_answer.id = original_id
            ans = dns_root_answer.Answer
            auth = dns_root_answer.Authority
            add = dns_root_answer.Additional

            # si la seccion answer NO viene vacía
            if ans != []:
                primer_rr_ans = dns_root_answer.get_first_ip_in_answer_type_A()
                if primer_rr_ans != None:  # si hay un mensaje tipo A
                    
                    # actualizamos el caché con la nueva direccion encontrada
                    print("se encontro una nueva ip, actualizando registros ...")
                    dominio = dns_root_answer.Qname
                    ip = primer_rr_ans[0]
                    print(f"ip encontrada:  {ip}")
                    actualizar_registros(registros_cache, dominio, ip)

                    return dns_root_answer  # retorna un objeto DNS_message

            # hay NS en authority
            elif auth != []:
                if dns_root_answer.get_first_ns_in_authority() != None:

                    if add != []:
                        first_RR__in_add = dns_root_answer.get_first_ip_in_additional_type_A()
                        if first_RR__in_add != None:
                            ip = first_RR__in_add[0]._data
                            ip = ".".join(map(str, ip))
                            new_address = (ip, puerto_DNS)
                            nombre_de_dominio = first_RR__in_add[1]
                            print("se encontro una nueva ip, actualizando registros ...")
                            actualizar_registros(registros_cache, nombre_de_dominio, ip)
                            return resolver(mensaje_consulta, original_id, new_address, nombre_de_dominio)

                    else:

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

                                    new_address = (name_server_ip, puerto_DNS)

                                    return resolver(mensaje_consulta, original_id, new_address, name_server[1])

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
        print(f"mensaje numero {contador_mensajes} ======================= ")
        print(f"cache actual: {registros_cache }")
        
        # recibimos el mensaje usando recvfrom
        recv_message, return_address = connection_socket.recvfrom(buff_size)

        parsed_recv_msg = parse_dns_message(recv_message)
        print("se recibió un mensaje ...")
        original_id = parsed_recv_msg.id

        # ----------------------------------------------------
        print("resolviendo query con resolver ....")

        msg_from_resolver = resolver(
            recv_message, original_id)  # recibe DNS_message

        if msg_from_resolver != None:
            print("entramos a retornar el mensaje final ...")
            response = msg_from_resolver.build_bytes_msg()
            connection_socket.sendto(response, return_address)
            print("se envió un mensaje al cliente ...")
        else:
            print(f"No se pudo responder al cliente")

        # seguimos esperando por si llegan otras conexiones
        contador_mensajes += 1


my_resolver()  # ejectutamos el resolver
