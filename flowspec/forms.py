from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy
from django.template.defaultfilters import filesizeformat

from flowspy.flowspec.models import * 
from ipaddr import *

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
        data = self.cleaned_data['source']
        if data:
            try:
                address = IPNetwork(data)
                return self.cleaned_data["source"]
            except Exception:
                raise forms.ValidationError('Invalid network address format')

    def clean_destination(self):
        data = self.cleaned_data['destination']
        if data:
            try:
                address = IPNetwork(data)
                return self.cleaned_data["destination"]
            except Exception:
                raise forms.ValidationError('Invalid network address format')

    def clean(self):
        source = self.cleaned_data.get('source', None)
        sourceports = self.cleaned_data.get('sourceport', None)
        ports = self.cleaned_data.get('port', None)
        destination = self.cleaned_data.get('destination', None)
        destinationports = self.cleaned_data.get('destinationport', None)
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
        return self.cleaned_data