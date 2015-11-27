from ipaddr import IPNetwork
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from peers.models import PeerRange, Peer
from flowspec.models import Route
from django.core.urlresolvers import reverse


def get_network(ip):
    try:
        address = IPNetwork(ip)
    except Exception:
        return (False, _('Invalid network address format'))
    else:
        return (True, address)


def clean_ip(address):
    if address.is_private:
            return _('Private addresses not allowed')

    if address.version == 4 and int(address.prefixlen) == 32:
        if int(address.network.compressed.split('.')[-1]) == 0:
            return _('Malformed address format. Cannot be ...0/32')
        elif int(address.network.compressed.split('.')[-1]) == 255:
            return _('Malformed address format. Cannot be ...255/32')


def clean_source(user, source):
    success, address = get_network(source)
    if not success:
        return address
    for net in settings.PROTECTED_SUBNETS:
        if address in IPNetwork(net):
            mail_body = "User %s %s attempted to set %s as the source address in a firewall rule" % (user.username, user.email, source)
            send_mail(
                settings.EMAIL_SUBJECT_PREFIX + "Caught an attempt to set a protected IP/network as a source address",
                mail_body,
                settings.SERVER_EMAIL,
                settings.NOTIFY_ADMIN_MAILS,
                fail_silently=True
            )
            return _('You have no authority on this subnet')
    return source


def clean_destination(user, destination):
    success, address = get_network(destination)
    if not success:
        return address
    for net in settings.PROTECTED_SUBNETS:
        if address in IPNetwork(net):
            mail_body = "User %s %s attempted to set %s as the destination address in a firewall rule" % (user.username, user.email, destination)
            send_mail(
                settings.EMAIL_SUBJECT_PREFIX + "Caught an attempt to set a protected IP/network as the destination address",
                mail_body, settings.SERVER_EMAIL,
                settings.NOTIFY_ADMIN_MAILS,
                fail_silently=True
            )
            return _('You have no authority on this subnet')
    # make sure its a network prefix that
    # can be used, depending on settings.PREFIX_LENGTH
    if address.prefixlen < settings.PREFIX_LENGTH:
        return _("Currently no prefix lengths < %s are allowed") % settings.PREFIX_LENGTH

    # make sure its a valid ip
    error = clean_ip(address)

    # make sure user can apply rule in these networks
    if error:
        return error
    if not user.is_superuser:
        networks = PeerRange.objects.filter(peer__in=user.userprofile.peers.all())
    else:
        networks = PeerRange.objects.filter(peer__in=Peer.objects.all()).distinct()
    network_is_mine = False
    for network in networks:
        net = IPNetwork(network.network)
        if IPNetwork(destination) in net:
            network_is_mine = True
    if not network_is_mine:
        return (_('Destination address/network should belong to your administrative address space. Check My Profile to review your networks'))
    return destination


def clean_expires(date):
    if date:
        range_days = (date - datetime.date.today()).days
        if range_days > 0 and range_days < 11:
            return date
        else:
            return _('Invalid date range')


def value_list_to_list(valuelist):
    vl = []
    for val in valuelist:
        vl.append(val[0])
    return vl


def get_matchingport_route_pks(portlist, routes):
    route_pk_list = []
    ports_value_list = value_list_to_list(portlist.values_list('port').order_by('port'))
    for route in routes:
        rsp = value_list_to_list(route.destinationport.all().values_list('port').order_by('port'))
        if rsp and rsp == ports_value_list:
            route_pk_list.append(route.pk)
    return route_pk_list


def get_matchingprotocol_route_pks(protocolist, routes):
    route_pk_list = []
    protocols_value_list = value_list_to_list(protocolist.values_list('protocol').order_by('protocol'))
    for route in routes:
        rsp = value_list_to_list(route.protocol.all().values_list('protocol').order_by('protocol'))
        if rsp and rsp == protocols_value_list:
            route_pk_list.append(route.pk)
    return route_pk_list


def clean_route_form(data):
    source = data.get('source', None)
    sourceports = data.get('sourceport', None)
    ports = data.get('port', None)
    then = data.get('then', None)
    destination = data.get('destination', None)
    destinationports = data.get('destinationport', None)
    user = data.get('applier', None)
    if (sourceports and ports):
        return _('Cannot create rule for source ports and ports at the same time. Select either ports or source ports')
    if (destinationports and ports):
        return _('Cannot create rule for destination ports and ports at the same time. Select either ports or destination ports')
    if sourceports and not source:
        return _('Once source port is matched, source has to be filled as well. Either deselect source port or fill source address')
    if destinationports and not destination:
        return _('Once destination port is matched, destination has to be filled as well. Either deselect destination port or fill destination address')
    if not (source or sourceports or ports or destination or destinationports):
        return _('Fill at least a Rule Match Condition')
    if not user.is_superuser and then[0].action not in settings.UI_USER_THEN_ACTIONS:
        return _('This action "%s" is not permitted') % (then[0].action)


def check_if_rule_exists(fields):
    routes = Route.objects.filter(
        source=fields.get('source'),
        destination=IPNetwork(fields.get('destination')).compressed,
    )
    for route in routes:
        return _('Rule exists with id %s and status %s. Please edit it.' % (route.id, route.status))
    return False
