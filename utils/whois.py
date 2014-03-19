# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2011-2014 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2011-2014 Leonidas Poulopoulos (@leopoul)
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

import socket
from ipaddr import *
import re
from django.conf import settings

def query(query, hostname, flags):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, 43))
    # as IPv6 is not supported by flowspec for the time ommit -T route6 
    s.send(" -i origin -r -K -T route " + query + "\r\n")
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
    routes = query(queryas,settings.PRIMARY_WHOIS, None)
    if not routes:
        routes = query(queryas,settings.ALTERNATE_WHOIS, None)
    return routes