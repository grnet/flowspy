# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright (C) 2017 CESNET a.l.e.
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

import re

def parse_portrange(s):
    """ Convert string s into array of ports.

Params:
    s(str) Port range in format like this: 80,100-120,443

Returns:
    list of str(int) or None on error
"""

    regexp = re.compile(r"^[1-9][0-9]*([-,][1-9][0-9]*)*$")
    r = re.match(regexp, s)
    if r:
        res = []
        pranges = s.split(",")
        for pr in pranges:
            ports = pr.split("-")
            if len(ports) == 1:
                res.append(ports[0])
            elif len(ports) == 2:
                res += [ str(i) for i in range(int(ports[0]), int(ports[1]) + 1) ]
        return res
    else:
        return None

if __name__ == "__main__":
    for i in ["1", "10-200", "1,10-20,150-200",
        "1,10-200,5080"]:
        print(i, parse_portrange(i))
    for i in ["i", "1,1o-s00,5080", "011-123-", "-123", "10-"]:
        print(i, parse_portrange(i))

