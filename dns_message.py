import dnslib.dns
from dnslib import DNSRecord, DNSQuestion, DNSHeader,  QTYPE
import socket
from dns_message import *
from dnslib.dns import RR, A


# ==============================================
""" Clase DNS_message que guarda informacion extraida de un mensaje dns """


class DNS_message:
    def __init__(self, id,  Qname,  ANCOUNT, NSCOUNT, ARCOUNT, Answer=[], Authority=[], Additional=[], Qtype=QTYPE.A):
        self.id = id
        self.Qtype = Qtype
        self.Qname = Qname
        self.ANCOUNT = ANCOUNT
        self.NSCOUNT = NSCOUNT
        self.ARCOUNT = ARCOUNT
        self.Answer = Answer
        self.Authority = Authority
        self.Additional = Additional

    def get_first_ip_in_answer_type_A(self):
        for i in range(len(self.Answer)):
            i_ans_record = self.Answer[i]  # objeto tipo dnslib.dns.RR


            # buscamos la ip de un record A

            # para saber si esto es asi debemos revisar el tipo de record
            ar_type = QTYPE.get(i_ans_record.rclass)

            if ar_type == 'A':  # si el tipo es 'A' (Address)
                i_add_record_rname = i_ans_record.rname  # nombre de dominio
                i_add_record_rdata = i_ans_record.rdata  # IP asociada
                return i_add_record_rdata, i_add_record_rname

        return None

    def get_first_ip_in_additional_type_A(self):

        for i in range(len(self.Additional)):
            i_add_record = self.Additional[i]  # objeto tipo dnslib.dns.RR

            # buscamos la ip de un record A

            # para saber si esto es asi debemos revisar el tipo de record
            ar_type = QTYPE.get(i_add_record.rclass)

            if ar_type == 'A':  # si el tipo es 'A' (Address)
                i_add_record_rname = i_add_record.rname  # nombre de dominio
                i_add_record_rdata = i_add_record.rdata  # IP asociada
                return i_add_record_rdata, i_add_record_rname

        return None

    def get_first_ns_in_authority(self):
        for i in range(len(self.Authority)):
            # objeto tipo dnslib.dns.RR
            authority_section_i = self.Authority[i]

            authority_section_i_rdata = authority_section_i.rdata
            authority_section_i_rname = authority_section_i.rname

            # si recibimos un registro tipo NS
            if isinstance(authority_section_i_rdata, dnslib.dns.NS):
                # entonces authority_section_0_rdata contiene el nombre de dominio del primer servidor de nombre de la lista

                return authority_section_i_rdata, authority_section_i_rname
        return None

    def build_dns_record(self):
        # agregamos qname
        dns_record = DNSRecord(q=DNSQuestion(self.Qname, self.Qtype))
        dns_record.header = DNSHeader(rd=0)  # recursion no habilitada
        dns_record.header.id = self.id

        # agregamos answer
        for ans in self.Answer:
            dns_record.add_answer(ans)

        # agregamos authority
        for auth in self.Authority:
            dns_record.add_auth(auth)

        # agregamos additional
        for add in self.Additional:
            dns_record.add_ar(add)

        return dns_record

    def build_bytes_msg(self):
        # pasamos de dns record a binario
        dns_record = self.build_dns_record()
        return bytes(dns_record.pack())

    def __str__(self):

        anss = ""
        space = "           "
        for ans in self.Answer:
            anss += f'{space}{str(ans)},\n'
        auths = ""

        for auth in self.Authority:
            auths += f'{space}{str(auth)},\n'
        adds = ""
        for add in self.Additional:
            adds += f'{space}{str(add)},\n'

        return f"DNS Message: ==================\n\
            ID: {self.id}\n\
            Qname: {self.Qname}\n\
            Qtype: {self.Qtype}\n\
            ANCOUNT: {self.ANCOUNT}\n\
            NSCOUNT: {self.NSCOUNT}\n\
            ARCOUNT: {self.ARCOUNT}\n\
            Answer: [\n{anss}]\n\
            Authority: [\n{auths}]\n\
            Additional: [\n{adds}]"


# ==============================================
""" Funcion que recibe un mensaje dns sin procesar y entrega
una objeto DNS_message con sus componentes """


def parse_dns_message(raw_message):
    dns_msg = DNSRecord.parse(raw_message)

    dns_id = dns_msg.header.id
    question = dns_msg.q
    qname = question.get_qname()
    ancount = dns_msg.header.a
    nscount = dns_msg.header.auth
    arcount = dns_msg.header.ar

    answer = dns_msg.rr
    authority = dns_msg.auth
    additional = dns_msg.ar

    return DNS_message(dns_id, qname, ancount, nscount, arcount, answer, authority, additional)

# ==============================================
""" Funcion que recibe un DNSRecord y entrega
una objeto DNS_message con sus componentes """


def parse_dns_record(dnsrecord_message):

    dns_id = dnsrecord_message.header.id
    question = dnsrecord_message.q
    qname = question.get_qname()
    ancount = dnsrecord_message.header.a
    nscount = dnsrecord_message.header.auth
    arcount = dnsrecord_message.header.ar

    answer = dnsrecord_message.rr
    authority = dnsrecord_message.auth
    additional = dnsrecord_message.ar

    return DNS_message(dns_id, qname, ancount, nscount, arcount, answer, authority, additional)


# ==============================================
""" retorna DNS_message o None """


def send_dns_message(address, message_in_bytes, buffer_size: int, wait_for_response: bool, debug: bool = False):
    # no orientado a conexion
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    response = None
    try:
        if debug:
            print(f"enviando mensaje a {address} ...")
        sock.sendto(message_in_bytes, address)
        if debug:
            print("mensaje enviado ...")
        if wait_for_response:
            if debug:
                print("recibiendo respuesta ...")
            data, _ = sock.recvfrom(buffer_size)
            if debug:
                print("parseando respuesta ...")
            response = parse_dns_message(data)
    finally:
        if debug:
            print("cerrando conexión ...")
        sock.close()
        if debug:
            print("conexión cerrada ...")

    return response


# ==============================================

def create_answer_message(qname, ip_answer, id, DNSRecord_query):
    dns_record = DNSRecord_query

    # dns_record = DNSRecord(q=DNSQuestion(qname, QTYPE.A))
    # dns_record.header = DNSHeader(rd=0)  # recursion no habilitada
    # dns_record.header.id = id

    # Modificar el mensaje de pregunta
    #dns_record.add_answer(RR(qname, QTYPE.A, rdata=A(ip_answer)))
    dns_record.add_answer(*RR.fromZone("{} A {}".format(qname, ip_answer)))

    return dns_record