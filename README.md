[![Documentation Status](https://readthedocs.org/projects/flowspy/badge/?version=latest)](https://readthedocs.org/projects/flowspy/?badge=latest)

# Firewall on Demand

## Description

Firewall on Demand applies via NETCONF, flow rules to a network
device. These rules are then propagated via e-bgp to peering routers.
Each user is authenticated against shibboleth. Authorization is
performed via a combination of a Shibboleth attribute and the peer
network address range that the user originates from. FoD is meant to
operate over this architecture:

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
flowspec capable routers. Of course FoD could apply rules directly
(via NETCONF always) to a router and then ibgp would do the rest. In
GRNET's case the flowspec capable device is an EX4200.

**Attention**: Make sure your FoD server has SSH access to your flowspec device.

## Documentation

You can find detailed documentation including installation / configuration
examples at [Flowspy documentation](http://flowspy.readthedocs.org).

## Installation Considerations

If you are upgrading from a previous version bear in mind the changes
introduced in Django 1.4.

## Rest Api
FoD provides a rest api. It uses token as authentication method. For usage
instructions & examples check the documentation.

## Limitations

A user can belong to more than one `Peer` without any limitations.
FoD UI polls the server to dynamically update the dashboard and the
"Live Status" about the `Route`s they are aware of. In addition, the polling
implementation fetches information for every `Peer` the user is associated
with. Thus, if a user belongs to many `Peer`s too many AJAX calls will be sent
to the backend which may result in a non responsive state. It is recommended to
keep the peers associated with any user under 5.


## Contact 

You can contact us directly at dev{at}noc[dot]grnet(.)gr

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
