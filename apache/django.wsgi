import os
import sys

sys.path.append('/home/leopoul/projects/')
sys.path.append('/home/leopoul/projects/flowspy')

os.environ['DJANGO_SETTINGS_MODULE'] = 'flowspy.settings'

from gevent import monkey; monkey.patch_all()


import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
