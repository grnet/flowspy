from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('flowspy.poller.views',
                       ('^$', 'main'),
                       ('^a/message/existing$', 'message_existing'),
                       ('^a/message/new$', 'message_new'),
                       ('^a/message/updates$', 'message_updates'))

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)', 'django.views.static.serve',\
        {'document_root':  settings.STATIC_URL}),
)
