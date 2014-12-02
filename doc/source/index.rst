.. fod documentation master file, created by
   sphinx-quickstart on Wed Oct 16 17:20:20 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

******************
Firewall on Demand
******************

Description
===========
Firewall on Demand applies, via Netconf, flow rules to a network device. These rules are then propagated via e-bgp to peering routers. Each user is authenticated against shibboleth. Authorization is performed via a combination of a Shibboleth attribute and the peer network address range that the user originates from.
FoD is meant to operate over this architecture::

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

NETCONF is chosen as the mgmt protocol to apply rules to a single flowspec capable device. Rules are then propagated via igbp to all flowspec capable routers. Of course FoD could apply rules directly (via NETCONF always) to a router and then ibgp would do the rest.
In GRNET's case the flowspec capable device is an EX4200.

.. attention::
	Make sure your FoD server has ssh access to your flowspec device.

.. attention::
   Installation instructions assume a clean Debian Wheezy with Django 1.4
   
Contact
=======
You can find more about FoD or raise your issues at `GRNET FoD repository <https://code.grnet.gr/projects/flowspy>`_ or `GRNET FoD Github repo <https://github.com/grnet/flowspy>`_ .

You can contact us directly at grnet{at}noc[dot]grnet(.)gr

Install
=======

.. toctree::
   :maxdepth: 2

   install


