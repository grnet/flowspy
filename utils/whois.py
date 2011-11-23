import socket
from ipaddr import *
import re

RIPEWHOIS = 'whois.ripe.net'
GRNETWHOIS = 'whois.grnet.gr'

def query(query, hostname, flags):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, 43))
    s.send(" -i origin -r -K -T route -T route6 " + query + "\r\n")
    response = ''
    while True:
        d = s.recv(4096)
        response += d
        if not d:
            break
    s.close()
    query = response.splitlines()
    routes4 = []
    routes6 = []
    final_routes4 = []
    final_routes6 = []
    for line in query:
        m = re.match(r"(^route6?\:\s+)(?P<subnets>\S+)", line)
        if m:
            if IPNetwork(m.group('subnets')).version == 4:
                routes4.append(IPNetwork(m.group('subnets')))
            if IPNetwork(m.group('subnets')).version == 6:
                routes6.append(IPNetwork(m.group('subnets')))
    final_routes = []
    if len(routes4):
        final_routes4 = collapse_address_list(routes4)
    if len(routes6):
        final_routes6 = collapse_address_list(routes6)
    final_routes = final_routes4 + final_routes6
    return final_routes

def whois(queryas):
    routes = query(queryas,GRNETWHOIS, None)
    if not routes:
        routes = query(queryas,RIPEWHOIS, None)
    return routes