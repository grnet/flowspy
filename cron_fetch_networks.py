#!/usr/bin/env python
import os
import sys

def populate_networks():
    peers = Peer.objects.all()
    for peer in peers:
        peer.fill_networks()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowspy.settings")
    from django.core.mail import send_mail
    from peers.models import *
    populate_networks()
