from django.core.management import setup_environ  
import settings
setup_environ(settings)
from django.core.mail import send_mail
from flowspy.peers.models import *


def populate_networks():
    peers = Peer.objects.all()
    for peer in peers:
        peer.fill_networks()
#    if peer_networks > 0:
#        send_mail('Peer networks added , 'noreply@grnet.gr', ['leopoul@noc.grnet.gr'])


if __name__ == "__main__":
    populate_networks()
