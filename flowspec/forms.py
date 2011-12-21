from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.template.defaultfilters import filesizeformat
from flowspy.flowspec.models import *
from ipaddr import *
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from django.core.mail import mail_admins, mail_managers, send_mail


class RouteForm(forms.ModelForm):
#    name = forms.CharField(help_text=ugettext_lazy("A unique route name,"
#                                         " e.g. uoa_block_p80"), label=ugettext_lazy("Route Name"), required=False)
#    source = forms.CharField(help_text=ugettext_lazy("A qualified IP Network address. CIDR notation,"
#                                         " e.g.10.10.0.1/32"), label=ugettext_lazy("Source Address"), required=False)
#    source_ports = forms.ModelMultipleChoiceField(queryset=MatchPort.objects.all(), help_text=ugettext_lazy("A set of source ports to block"), label=ugettext_lazy("Source Ports"), required=False)
#    destination = forms.CharField(help_text=ugettext_lazy("A qualified IP Network address. CIDR notation,"
#                                         " e.g.10.10.0.1/32"), label=ugettext_lazy("Destination Address"), required=False)
#    destination_ports = forms.ModelMultipleChoiceField(queryset=MatchPort.objects.all(), help_text=ugettext_lazy("A set of destination ports to block"), label=ugettext_lazy("Destination Ports"), required=False)
#    ports = forms.ModelMultipleChoiceField(queryset=MatchPort.objects.all(), help_text=ugettext_lazy("A set of ports to block"), label=ugettext_lazy("Ports"), required=False)

    class Meta:
        model = Route
    
    def clean_source(self):
        user = User.objects.get(pk=self.data['applier'])
        peer = user.get_profile().peer
        data = self.cleaned_data['source']
        private_error = False
        protected_error = False
        if data:
            try:
                address = IPNetwork(data)
                for net in settings.PROTECTED_SUBNETS:
                    if address in IPNetwork(net):
                        protected_error = True
                        mail_body = "User %s %s (%s) attempted to set %s as the source address in a firewall rule" %(user.username, user.email, peer.peer_name, data)
                        send_mail(settings.EMAIL_SUBJECT_PREFIX + "Caught an attempt to set a protected IP/network as a source address",
                              mail_body, settings.SERVER_EMAIL,
                              [settings.NOC_MAIL], fail_silently=True)
                        raise forms.ValidationError("Not allowed")
                if address.is_private:
                    private_error = True
                    raise forms.ValidationError('Private addresses not allowed')
                else:
                    return self.cleaned_data["source"]
            except Exception:
                error_text = 'Invalid network address format'
                if private_error:
                    error_text = 'Private addresses not allowed'
                if protected_error:
                    error_text = 'You have no authority on this subnet'
                raise forms.ValidationError(error_text)

    def clean_destination(self):
        user = User.objects.get(pk=self.data['applier'])
        peer = user.get_profile().peer        
        data = self.cleaned_data['destination']
        error = None
        protected_error = False
        if data:
            try:
                address = IPNetwork(data)
                for net in settings.PROTECTED_SUBNETS:
                    if address in IPNetwork(net):
                        protected_error = True
                        mail_body = "User %s %s (%s) attempted to set %s as the destination address in a firewall rule" %(user.username, user.email, peer.peer_name, data)
                        send_mail(settings.EMAIL_SUBJECT_PREFIX + "Caught an attempt to set a protected IP/network as the destination address",
                              mail_body, settings.SERVER_EMAIL,
                              [settings.NOC_MAIL], fail_silently=True)
                        raise forms.ValidationError("Not allowed")
                if address.prefixlen < settings.PREFIX_LENGTH:
                    error = "Currently no prefix lengths < %s are allowed" %settings.PREFIX_LENGTH
                    raise forms.ValidationError('error')
                return self.cleaned_data["destination"]
            except Exception:
                error_text = 'Invalid network address format'
                if error:
                    error_text = error
                if protected_error:
                    error_text = 'You have no authority on this subnet'
                raise forms.ValidationError(error_text)
    
    def clean_expires(self):
        date = self.cleaned_data['expires']
        if date:
            range_days = (date - datetime.date.today()).days
            if range_days > 0 and range_days < 11:
                return self.cleaned_data["expires"]
            else:
                raise forms.ValidationError('Invalid date range')

    def clean(self):
        name = self.cleaned_data.get('name', None)
        source = self.cleaned_data.get('source', None)
        sourceports = self.cleaned_data.get('sourceport', None)
        ports = self.cleaned_data.get('port', None)
        then = self.cleaned_data.get('then', None)
        destination = self.cleaned_data.get('destination', None)
        destinationports = self.cleaned_data.get('destinationport', None)
        user = self.cleaned_data.get('applier', None)
        peer = user.get_profile().peer
        networks = peer.networks.all()
        mynetwork = False
        route_pk_list = []
        if destination:
            for network in networks:
                net = IPNetwork(network.network)
                if IPNetwork(destination) in net:
                    mynetwork = True
            if not mynetwork:
                 raise forms.ValidationError('Destination address/network should belong to your administrative address space. Check My Profile to review your networks')
        if (sourceports and ports):
            raise forms.ValidationError('Cannot create rule for source ports and ports at the same time. Select either ports or source ports')
        if (destinationports and ports):
            raise forms.ValidationError('Cannot create rule for destination ports and ports at the same time. Select either ports or destination ports')
        if sourceports and not source:
            raise forms.ValidationError('Once source port is matched, source has to be filled as well. Either deselect source port or fill source address')
        if destinationports and not destination:
            raise forms.ValidationError('Once destination port is matched, destination has to be filled as well. Either deselect destination port or fill destination address')
        if not (source or sourceports or ports or destination or destinationports):
            raise forms.ValidationError('Fill at least a Route Match Condition')
        if not user.is_superuser and then[0].action not in settings.UI_USER_THEN_ACTIONS:
            raise forms.ValidationError('This action "%s" is not permitted' %(then[0].action))
        existing_routes = Route.objects.exclude(status='EXPIRED').exclude(status='PENDING').exclude(status='ERROR').exclude(status='ADMININACTIVE')
        existing_routes = existing_routes.filter(applier__userprofile__peer=peer)
        if source:
            source = IPNetwork(source).compressed
            existing_routes = existing_routes.filter(source=source)
        else:
            existing_routes = existing_routes.filter(source=None)
        if sourceports:
            route_pk_list=get_matchingport_route_pks(sourceports, existing_routes)
            if route_pk_list:
                existing_routes = existing_routes.filter(pk__in=route_pk_list)
        else:
            existing_routes = existing_routes.filter(sourceport=None)
        if destinationports:
            route_pk_list=get_matchingport_route_pks(destinationports, existing_routes)
            if route_pk_list:
                existing_routes = existing_routes.filter(pk__in=route_pk_list)
        else:
            existing_routes = existing_routes.filter(destinationport=None)
        if ports:
            route_pk_list=get_matchingport_route_pks(ports, existing_routes)
            if route_pk_list:
                existing_routes = existing_routes.filter(pk__in=route_pk_list)              
        else:
            existing_routes = existing_routes.filter(port=None)
        
        for route in existing_routes:
            if name != route.name:
                existing_url = reverse('edit-route', args=[route.name])
                if IPNetwork(destination) in IPNetwork(route.destination) or IPNetwork(route.destination) in IPNetwork(destination):
                    raise forms.ValidationError('Found an exact %s rule, %s with destination prefix %s<br>To avoid overlapping try editing rule <a href=\'%s\'>%s</a>' %(route.status, route.name, route.destination, existing_url, route.name))
        return self.cleaned_data

class ThenPlainForm(forms.ModelForm):
#    action = forms.CharField(initial='rate-limit')
    class Meta:
        model = ThenAction
    
    def clean_action_value(self):
        action_value = self.cleaned_data['action_value']
        if action_value:
            try:
                assert(int(action_value))
                if int(action_value) < 50:
                    raise forms.ValidationError('Rate-limiting cannot be < 50kbps')
                return "%s" %self.cleaned_data["action_value"]
            except:
                raise forms.ValidationError('Rate-limiting should be an integer < 50')
        else:
            raise forms.ValidationError('Cannot be empty')

    def clean_action(self):
        action = self.cleaned_data['action']
        if action != 'rate-limit':
            raise forms.ValidationError('Cannot select something other than rate-limit')
        else:
            return self.cleaned_data["action"]
    

class PortPlainForm(forms.ModelForm):
#    action = forms.CharField(initial='rate-limit')
    class Meta:
        model = MatchPort
    
    def clean_port(self):
        port = self.cleaned_data['port']
        if port:
            try:
                assert(int(port))
                return "%s" %self.cleaned_data["port"]
            except:
                raise forms.ValidationError('Port should be an integer')
        else:
            raise forms.ValidationError('Cannot be empty')

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