[![Documentation Status](https://readthedocs.org/projects/flowspy/badge/?version=latest)](https://readthedocs.org/projects/flowspy/?badge=latest)

#Firewall on Demand#

##Description##

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

**Attention**: Make sure your FoD server has ssh access to your flowspec device.

##Installation Considerations##

You can find the installation instructions for Debian Wheezy (64)
with Django 1.4.x at [Flowspy documentation](http://flowspy.readthedocs.org).
If upgrading from a previous version bear in mind the changes introduced in Django 1.4.


##Rest Api##
FoD provides a rest api. It uses token as authentication method.

### Generating Tokens
A user can generate a token for his account on "my profile" page from FoD's
UI. Then by using this token in the header of the request he can list, retrieve,
modify and create rules.

### Example Usage
Here are some examples:

#### GET items
- List all the rules your user has created (admin users can see all the rules)

            curl -X GET https://fod.example.com/api/routes/ -H 'Authorization: Token <Your users token>'

- Retrieve a specific rule:

            curl -X GET https://fod.example.com/api/routes/<rule_id>/ -H 'Authorization: Token <Your users token>'

- In order to create or modify a rule you have to use POST/PUT methods.

#### POST/PUT rules
In order to update or create rules you can follow this example:

##### Foreign Keys
In order to create/modify a rule you have to connect the rule with some foreign keys:

###### Ports, Fragmentypes, protocols, thenactions
When creating a rule, one can specify:

- source port
- destination port
- port (if source = destination)

That can be done by getting the url of the desired port instance from `/api/ports/<port_id>/`

Same with Fragmentypes in `/api/fragmenttypes/<fragmenttype_id>/`, protocols in `/api/matchprotocol/<protocol_id>/` and then actions in `/api/thenactions/<action_id>/`.

Since we have the urls we want to connect with the rule we want to create, we can make a POST request like the following:


      curl -X POST -H 'Authorization: Token <Your users token>' -F "name=Example" -F "comments=Description" -F "source=0.0.0.0/0" -F "sourceport=https://fod.example.com/api/ports/7/" -F "destination=203.0.113.12" https://fod.example.com/api/routes/

And here is a PUT request example:

      curl -X PUT -F "name=Example" -F "comments=Description" -F "source=0.0.0.0/0" -F "sourceport=https://fod.example.com/api/ports/7/" -F "destination=83.212.9.93" https://fod.example.com/api/routes/12/ -H  'Authorization: Token <Your users token>'


##Limitations##

A user can belong to more than one peer, without any limitation. This fact may
produce some limitations though, to FoD application. FoD uses polling for updating
dashboard and let users know about other users' actions, who belong to the same
peer. In order to fetch updates from all user's peers, FoD makes ajax calls for
any one of them. It is recommended not to add more than 5 peers to any user,
because it may cause malfunction to FoD application.


##Contact##

You can find more about FoD or raise your issues at GRNET FoD
repository: [GRNET repo](https://code.grnet.gr/fod) or [Github repo](https://github.com/grnet/flowspy).

You can contact us directly at dev{at}noc[dot]grnet(.)gr

## Copyright and license

Copyright © 2010-2014 Greek Research and Technology Network (GRNET S.A.)

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
