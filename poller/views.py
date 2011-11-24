from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

import uuid
import simplejson
import datetime
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponse
from gevent.event import Event
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from flowspy.utils import beanstalkc

import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_message(from_, body):
    data = {'id': str(uuid.uuid4()), 'from': from_, 'body': body}
    data['html'] = render_to_string('poll_message.html', dictionary={'message': data})
    return data


def json_response(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    return HttpResponse(simplejson.dumps(value), **kwargs)

class Msgs(object):
    cache_size = 200

    def __init__(self):
        self.cache = []
        self.new_message_event = Event()

    def main(self, request):
        if self.cache:
            request.session['cursor'] = self.cache[-1]['id']
        return render_to_response('poll.html', {'messages': self.cache})
    
    @csrf_exempt
    def message_existing(self, request):
        if self.cache:
            request.session['cursor'] = self.cache[-1]['id']
        return json_response({'messages': self.cache})
    
    @csrf_exempt
    def message_new(self, request=None, mesg=None):
        if request:
            name = request.META.get('REMOTE_ADDR') or 'Anonymous'
            forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if forwarded_for and name == '127.0.0.1':
                name = forwarded_for
            msg = create_message(name, request.POST['body'])
        if mesg:
            message = mesg
            now = datetime.datetime.now()
            msg = create_message("[%s]"%now.strftime("%Y-%m-%d %H:%M:%S"), message)
        self.cache.append(msg)
        if len(self.cache) > self.cache_size:
            self.cache = self.cache[-self.cache_size:]
        self.new_message_event.set()
        self.new_message_event.clear()
        return json_response(msg)
    
    @csrf_exempt
    def message_updates(self, request):
        cursor = request.session.get('cursor')
        if not self.cache or cursor == self.cache[-1]['id']:
            self.new_message_event.wait()
        assert cursor != self.cache[-1]['id'], cursor
        try:
            for index, m in enumerate(self.cache):
                if m['id'] == cursor:
                    return json_response({'messages': self.cache[index + 1:]})
            return json_response({'messages': self.cache})
        finally:
            if self.cache:
                request.session['cursor'] = self.cache[-1]['id']
            else:
                request.session.pop('cursor', None)

    def monitor_polls(self, polls=None):
        b = beanstalkc.Connection()
        b.watch(settings.POLLS_TUBE)
        while True:
            job = b.reserve()
            msg = job.body
            job.bury()
            self.message_new(None, msg)
            
    
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










