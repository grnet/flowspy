# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gevent
import json

import uuid
import datetime
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse
from gevent.event import Event
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from peers.models import Peer

import beanstalkc

import logging
import os

LOG_FILENAME = os.path.join(settings.LOG_FILE_LOCATION, 'poller.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(formatter)
logger.addHandler(handler)


def create_message(message, user, time):
    data = {'id': str(uuid.uuid4()), 'body': message, 'user':user, 'time':time}
    data['html'] = render_to_string('poll_message.html', dictionary={'message': data})
    return data


def json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    return HttpResponse(json.dumps(value), **kwargs)


class Msgs(object):
    cache_size = 500

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Msgs, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        logger.info("initializing")
        self.user = None
        self.user_cache = {}
        self.user_cursor = {}
        self.cache = []
        self.new_message_event = None
        self.new_message_user_event = {}

    def main(self, request):
        if self.user_cache:
            request.session['cursor'] = self.user_cache[-1]['id']
        return render_to_response('poll.html', {'messages': self.user_cache})

    def message_existing(self, request, peer_id):
        if request.is_ajax():
            try:
                user = Peer.objects.get(pk=peer_id).peer_tag
            except:
                user = None
                return False
            try:
                assert(self.new_message_user_event[user])
            except:
                self.new_message_user_event[user] = Event()
            try:
                if self.user_cache[user]:
                    self.user_cursor[user] = self.user_cache[user][-1]['id']
            except:
                self.user_cache[user] = []
                self.user_cursor[user] = ''
            return json_response({'messages': self.user_cache[user]})
        return HttpResponseRedirect(reverse('group-routes'))

    def message_new(self, mesg=None):
        if mesg:
            message = mesg['message']
            user = mesg['username']
            logger.info("from %s" %user)
            now = datetime.datetime.now()
            msg = create_message(message, user, now.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            isinstance(self.user_cache[user], list)
        except:
            self.user_cache[user] = []
        self.user_cache[user].append(msg)
        if self.user_cache[user][-1] == self.user_cache[user][0]:
            self.user_cursor[user] = self.user_cache[user][-1]['id']
        else:
            self.user_cursor[user] = self.user_cache[user][-2]['id']
        if len(self.user_cache[user]) > self.cache_size:
            self.user_cache[user] = self.user_cache[user][-self.cache_size:]
        try:
            assert(self.new_message_user_event[user])
        except:
            self.new_message_user_event[user] = Event()
        self.new_message_user_event[user].set()
        self.new_message_user_event[user].clear()
        return json_response(msg)

    def message_updates(self, request, peer_id):
        if request.is_ajax():
            cursor = {}
            try:
                user = Peer.objects.get(pk=peer_id).peer_tag
            except:
                user = None
                return False
            try:
                cursor[user] = self.user_cursor[user]
            except:
                return HttpResponse(content='', content_type=None, status=400)

            try:
                if not isinstance(self.user_cache[user], list):
                    self.user_cache[user] = []
            except:
                self.user_cache[user] = []
            if not self.user_cache[user] or cursor[user] == self.user_cache[user][-1]['id']:
                self.new_message_user_event[user].wait(settings.POLL_SESSION_UPDATE)
            try:
                for index, m in enumerate(self.user_cache[user]):
                    if m['id'] == cursor[user]:
                        return json_response({'messages': self.user_cache[user][index + 1:]})
                return json_response({'messages': self.user_cache[user]})
            finally:
                if self.user_cache[user]:
                    self.user_cursor[user] = self.user_cache[user][-1]['id']
        return HttpResponseRedirect(reverse('group-routes'))

    def monitor_polls(self):
        b = beanstalkc.Connection()
        b.watch(settings.POLLS_TUBE)
        while True:
            job = b.reserve()
            msg = json.loads(job.body)
            job.bury()
            logger.info("Got New message")
            self.message_new(msg)

    def start_polling(self):
        logger.info("Start Polling")
        gevent.spawn(self.monitor_polls)


msgs = Msgs()
main = msgs.main

message_updates = msgs.message_updates
message_existing = msgs.message_existing


poll = msgs.start_polling
poll()
