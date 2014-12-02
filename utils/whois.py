# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

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