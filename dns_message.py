from dnslib import DNSRecord, DNSQuestion, A, AAAA, NS

# ==============================================
""" Clase DNS_message que guarda informacion extraida de un mensaje dns """


class DNS_message:
    def __init__(self,id,  Qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer=[], Authority=[], Additional=[]):
        self.id = id
        self.Qname = Qname
        self.ANCOUNT = ANCOUNT
        self.NSCOUNT = NSCOUNT
        self.ARCOUNT = ARCOUNT
        self.Answer = Answer
        self.Authority = Authority
        self.Additional = Additional

    def get_first_ip_in_additional_type_A(self):
        for rr in self.Additional:
            if isinstance(rr, A):
                return rr.rdata
        return None

    def get_first_ns_in_authority(self):
        for auth in self.Authority:
            if isinstance(auth, NS):
                return auth.rdata.label
        return None

    def build_dns_record(self):

        dns_record = DNSRecord(id=self.id)
        # agregamos qname
        qname = self.Qname.encode('utf-8')
        dns_record.add_question(DNSQuestion(qname))

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
