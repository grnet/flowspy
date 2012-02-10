# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab
from django.core.management.base import BaseCommand, CommandError
from flowspy.peers.models import *

class Command(BaseCommand):
    args = ''
    help = 'Fetches networks for each peer in database'

    def handle(self, *args, **options):
        for p in Peer.objects.all():
            self.stdout.write('Fetching networks for %s...' % p.peer_name.encode('utf8'))
            p.fill_networks()
            self.stdout.write('done\n')
        self.stdout.write('Finished!\n')