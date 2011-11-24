#!/usr/bin/python
from gevent.wsgi import WSGIServer
from poller.application import application
print 'Serving on 8000...'
WSGIServer(('netdev.grnet.gr', 9090), application).serve_forever()
