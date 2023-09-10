from dnslib import DNSRecord

""" Clase DNS_message que guarda informacion extraida de un mensaje dns """

class DNS_message:
    def __init__(self, Qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional):
        self.Qname = Qname
        self.ANCOUNT = ANCOUNT
        self.NSCOUNT = NSCOUNT
        self.ARCOUNT = ARCOUNT
        self.Answer = Answer
        self.Authority = Authority
        self.Additional = Additional

    def __str__(self):
        return f"DNS Message: ==================\n\
            Qname: {self.Qname}\n\
            ANCOUNT: {self.ANCOUNT}\n\
            NSCOUNT: {self.NSCOUNT}\n\
            ARCOUNT: {self.ARCOUNT}\n\
            Answer: {self.Answer}\n\
            Authority: {self.Authority}\n\
            Additional: {self.Additional}"
            

# ==============================================
def parse_dns_message(raw_message):
    dns_msg = DNSRecord.parse(raw_message)
    
    qname = dns_msg.q.qname
    
    ancount = dns_msg.header.a
    nscount = dns_msg.header.auth
    arcount = dns_msg.header.ar

    answer = dns_msg.rr   
    authority = dns_msg.auth
    additional = dns_msg.ar

    
    return DNS_message(qname, ancount, nscount, arcount, answer, authority, additional)


# ==============================================

# def parse_dns_message(message):

#     header_length  = 12
#     caracter_fin_header = header_length * 2
#     header = message[:caracter_fin_header]  
#     body = message[caracter_fin_header:]

#     # sacamos los componentes del header
#     ARCOUNT = int(header[-4:-2], 16) # pasamos a enteros de 16 bits
#     NSCOUNT = int(header[-6:-4], 16)
#     ANCOUNT = int(header[-8:-6], 16)

#     # sacamos el Qname
#     fin_qname = b'\x00'
#     qname, rest = body.split(fin_qname, 1) # primera parte tiene qname, segunda inicia answer
#     qname = qname.decode()

#     # answer estaria al inicio de rest
#     answer_start = 4  # parte 4 desde rest
#     authority_start = answer_start + ANCOUNT  
#     additional_start = authority_start + NSCOUNT 

#     # Extraer las secciones Answer, Authority y Additional
#     answer = hex_message[answer_start:authority_start]
#     authority = hex_message[authority_start:additional_start]
#     additional = hex_message[additional_start:]

#     # creamos un DNS_message
#     dns_msg = DNS_message(qname, ANCOUNT, NSCOUNT, ARCOUNT, answer, authority, additional)

#     return dns_msg



# # Mensaje DNS en formato hexadecimal
# hex_message = 'X\x7f\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x07example\x03com\x00\x00\x01\x00\x01\x00\x00)\x04\xd0\x00\x00\x00\x00\x00\x0c\x00\n\x00\x08t\xc9\xdb|\xb0\xf8\x1f\xa4'
# binary_message = bytes.fromhex(hex_message)

# # Analizar el mensaje y crear la instancia de DNS_message
# dns_message = parse_dns_message(binary_message)

# # Imprimir la instancia de DNS_message
# print(dns_message.Qname)
# print(dns_message.ANCOUNT)
# print(dns_message.NSCOUNT)
# print(dns_message.ARCOUNT)
# print(dns_message.Answer)
