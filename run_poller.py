#!/usr/bin/python
from gevent.wsgi import WSGIServer
from poller.application import application
server="localhost"
port=8081
print 'Serving on port %s...' % port
WSGIServer((server,port ), application).serve_forever()
