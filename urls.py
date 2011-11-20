from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^flowspy/', include('flowspy.foo.urls')),
    url(r'^/?$', 'flowspy.flowspec.views.user_routes', name="user-routes"),
    url(r'^user/login/?', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name="login"),
    url(r'^user/logout/?', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    (r'^setlang/?$', 'django.views.i18n.set_language'),
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)', 'django.views.static.serve',\
            {'document_root':  settings.STATIC_URL}),
    )