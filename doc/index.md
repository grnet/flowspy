# Description

Firewall on Demand applies, via Netconf, flow rules to a network device.
These rules are then propagated via e-bgp to peering routers. Each user
is authenticated against shibboleth. Authorization is performed via a
combination of a Shibboleth attribute and the peer network address range
that the user originates from. FoD is meant to operate over this
architecture:

    +-----------+          +------------+        +------------+
    |   FoD     | NETCONF  | flowspec   | ebgp   |   router   |
    | web app   +----------> device     +-------->            |
    +-----------+          +------+-----+        +------------+
                                  | ebgp
                                  |
                           +------v-----+
                           |   router   |
                           |            |
                           +------------+

NETCONF is chosen as the mgmt protocol to apply rules to a single
flowspec capable device. Rules are then propagated via igbp to all
flowspec capable routers. Of course FoD could apply rules directly (via
NETCONF always) to a router and then ibgp would do the rest. In GRNET’s
case the flowspec capable device is an EX4200.

> ** Attention **
>
> Make sure your FoD server has SSH access to your flowspec device.

# Contact

You can find more about FoD or raise your issues at [Github FoD
repository].

You can contact us directly at dev{at}noc[dot]grnet(.)gr

# Repositories

  - [Github FoD repository](https://github.com/grnet/flowspy)


## Copyright and license

Copyright © 2010-2017 Greek Research and Technology Network (GRNET S.A.)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
