import dnslib.dns
from dnslib import DNSRecord, DNSQuestion, A, AAAA, NS, DNSHeader
from dnslib.dns import CLASS, QTYPE
from dnslib import DNSRecord, RR, QTYPE

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

        if self.Answer != []:
            # primer objeto en la lista all_resource_records
            first_answer = self.Answer.get_a()

            return first_answer.rdata  # rdata asociada a la respuesta

        return None

    def get_first_ip_in_additional_type_A(self):

        for i in range(len(self.Additional)):
            i_add_record = self.Additional[i]  # objeto tipo dnslib.dns.RR

            # buscamos la ip de un record A

            # para saber si esto es asi debemos revisar el tipo de record
            ar_type = QTYPE.get(i_add_record.rclass)

            if ar_type == 'A':  # si el tipo es 'A' (Address)
                # i_add_record_rname = i_add_record.rname  # nombre de dominio
                i_add_record_rdata = i_add_record.rdata  # IP asociada
                return i_add_record_rdata

        return None

    def get_first_ns_in_authority(self):
        for i in range(len(self.Authority)):
            # objeto tipo dnslib.dns.RR
            authority_section_i = self.Authority[i]

            authority_section_i_rdata = authority_section_i.rdata

            # si recibimos un registro tipo NS
            if isinstance(authority_section_i_rdata, dnslib.dns.NS):
                # entonces authority_section_0_rdata contiene el nombre de dominio del primer servidor de nombre de la lista
                name_server_domain = authority_section_i_rdata
                return name_server_domain

        return None

    def build_dns_record(self):
        # agregamos qname
        dns_record = DNSRecord(q=DNSQuestion(self.Qname, self.Qtype))
        dns_record.header = DNSHeader(rd=0) #recursion no habilitada
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
