import dnslib.dns
from dnslib import DNSRecord, DNSQuestion, A, AAAA, NS
from dnslib.dns import CLASS, QTYPE

# ==============================================
""" Clase DNS_message que guarda informacion extraida de un mensaje dns """


class DNS_message:
    def __init__(self, id,  Qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer=[], Authority=[], Additional=[]):
        self.id = id
        self.Qname = Qname
        self.ANCOUNT = ANCOUNT
        self.NSCOUNT = NSCOUNT
        self.ARCOUNT = ARCOUNT
        self.Answer = Answer
        self.Authority = Authority
        self.Additional = Additional
        
    def get_first_ip_in_answer_type_A(self):

        if self.Answer != []:
            first_answer = self.Answer.get_a()  # primer objeto en la lista all_resource_records

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
            authority_section_i = self.Authority[i]  # objeto tipo dnslib.dns.RR

            authority_section_i_rdata = authority_section_i.rdata

            if isinstance(authority_section_i_rdata, dnslib.dns.NS): # si recibimos un registro tipo NS
                name_server_domain = authority_section_i_rdata  # entonces authority_section_0_rdata contiene el nombre de dominio del primer servidor de nombre de la lista
                return name_server_domain
            
        return None

    def build_dns_record(self):

        dns_record = DNSRecord()
        # agregamos qname
        dns_record.question(self.Qname)
        # qname = (self.Qname).encode('utf-8')
        # dns_record.add_question(DNSQuestion(qname))

        # agregamos answer
        for ans in self.Answer:
            if ans.rtype == A:
                dns_record.add_answer(ans)

        # agregamos authority
        for auth in self.Authority:
            dns_record.add_auth(auth)

        # agregamos additional
        for add in self.Additional:
            if add.rtype == A or add.rtype == AAAA:
                dns_record.add_ar(add)

        return dns_record

    def build_binary_msg(self):
        # pasamos de dns record a binario
        dns_record = self.build_dns_record()
        return dns_record.pack()

    def __str__(self):

        anss = ""
        for ans in self.Answer:
            anss += '   '+str(ans) + ', ' + '\n'
        auths = ""

        for auth in self.Authority:
            auths += '   '+str(auth)+', ' + '\n'

        adds = ""
        for add in self.Additional:
            adds += '   '+str(add) + ', ' + '\n'

        return f"DNS Message: ==================\n\
            ID: {self.id}\n\
            Qname: {self.Qname}\n\
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

    qname = dns_msg.q.qname

    ancount = dns_msg.header.a
    nscount = dns_msg.header.auth
    arcount = dns_msg.header.ar

    answer = dns_msg.rr
    authority = dns_msg.auth
    additional = dns_msg.ar

    return DNS_message(dns_id, qname, ancount, nscount, arcount, answer, authority, additional)
