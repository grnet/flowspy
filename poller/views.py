#
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
#Copyright © 2011-2013 Greek Research and Technology Network (GRNET S.A.)

#Developed by Leonidas Poulopoulos (leopoul-at-noc-dot-grnet-dot-gr),
#GRNET NOC
#
#Permission to use, copy, modify, and/or distribute this software for any
#purpose with or without fee is hereby granted, provided that the above
#copyright notice and this permission notice appear in all copies.
#
#THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
#TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
#CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
#DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
#ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
#SOFTWARE.
#
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
import json

import uuid
import datetime
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse
from gevent.event import Event
from django.conf import settings
#from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


import beanstalkc

import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_message(body, user):
    data = {'id': str(uuid.uuid4()), 'body': body, 'user':user}
    data['html'] = render_to_string('poll_message.html', dictionary={'message': data})
    return data


def json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    return HttpResponse(json.dumps(value), **kwargs)

class Msgs(object):
    cache_size = 500

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

    def message_existing(self, request):
        if request.is_ajax():
            try:
                user = request.user.get_profile().peer.domain_name
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
            now = datetime.datetime.now()
            msg = create_message("[%s]: %s"%(now.strftime("%Y-%m-%d %H:%M:%S"),message), user)
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
        self.new_message_user_event[user].set()
        self.new_message_user_event[user].clear()
        return json_response(msg)
    
    def message_updates(self, request):
        if request.is_ajax():
            cursor = {}
            try:
                user = request.user.get_profile().peer.domain_name
            except:
                user = None
                return False
            try:
                cursor[user] = self.user_cursor[user]
            except:
                return HttpResponse(content='', mimetype=None, status=400)
                
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

    def monitor_polls(self, polls=None):
        b = beanstalkc.Connection()
        b.watch(settings.POLLS_TUBE)
        while True:
            job = b.reserve()
            msg = json.loads(job.body)
            job.bury()
            self.message_new(msg)
            
    
    def start_polling(self):
        logger.info("Start Polling")
        p = Pool(10)
        while True:
            p.spawn(self.monitor_polls)
            
msgs = Msgs()
main = msgs.main

message_new = msgs.message_new
message_updates = msgs.message_updates
message_existing = msgs.message_existing

poll = msgs.start_polling
poll()

