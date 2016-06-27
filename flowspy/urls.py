from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.contrib import admin
from rest_framework import routers
from flowspec.viewsets import (
    RouteViewSet,
    PortViewSet,
    ThenActionViewSet,
    FragmentTypeViewSet,
    MatchProtocolViewSet,
    MatchDscpViewSet,
)

admin.autodiscover()

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'routes', RouteViewSet, base_name='route')
router.register(r'ports', PortViewSet)
router.register(r'thenactions', ThenActionViewSet)
router.register(r'fragmentypes', FragmentTypeViewSet)
router.register(r'matchprotocol', MatchProtocolViewSet)
router.register(r'matchdscp', MatchDscpViewSet)


urlpatterns = patterns(
    '',
    (r'^poll/', include('poller.urls')),
    url(r'^/?$', 'flowspec.views.group_routes', name="group-routes"),
    url(r'^routes_ajax/?$', 'flowspec.views.group_routes_ajax', name="group-routes-ajax"),
    url(r'^overview_ajax/?$', 'flowspec.views.overview_routes_ajax', name="overview-ajax"),
    url(r'^dashboard/$', 'flowspec.views.dashboard', name="dashboard"),
    url(r'^profile/?$', 'flowspec.views.user_profile', name="user-profile"),
    url(r'^profile/token/$', 'accounts.views.generate_token', name="user-profile-token"),
    url(r'^add/?$', 'flowspec.views.add_route', name="add-route"),
    url(r'^addport/?$', 'flowspec.views.add_port', name="add-port"),
    url(r'^edit/(?P<route_slug>[\w\-]+)/$', 'flowspec.views.edit_route', name="edit-route"),
    url(r'^delete/(?P<route_slug>[\w\-]+)/$', 'flowspec.views.delete_route', name="delete-route"),
    url(r'^login/?', 'flowspec.views.user_login', name="login"),
    url(r'^welcome/?', 'flowspec.views.welcome', name="welcome"),
    url(r'^logout/?', 'flowspec.views.user_logout', name="logout"),
    (r'^setlang/?$', 'django.views.i18n.set_language'),
    url(r'^selectinst/?$', 'flowspec.views.selectinst', name="selectinst"),
    url(r'^accounts/activate/(?P<activation_key>\w+)/$', 'accounts.views.activate', name='activate_account'),
    url(r'^load_js/(?P<file>[\w\s\d_-]+)/$', 'flowspec.views.load_jscript', name="load-js"),
    url(
        r'^activate/complete/$',
        direct_to_template,
        {'template': 'registration/activation_complete.html'},
        name='registration_activation_complete'
    ),
    (r'^admin/', include(admin.site.urls)),
    (r'^tinymce/', include('tinymce.urls')),
    url(
        r'^altlogin/?',
        'django.contrib.auth.views.login',
        {'template_name': 'overview/login.html'}, name="altlogin"
    ),
    url(r'^overview/?$', 'flowspec.views.overview', name="overview"),
    url(r'^api/', include(router.urls)),
    url(r'^details/(?P<route_slug>[\w\-]+)/$', 'flowspec.views.routedetails', name="route-details"),
)

if 'graphs' in settings.INSTALLED_APPS:
    from graphs import urls as graphs_urls
    urlpatterns += (
        '', url(r'^graphs/', include(graphs_urls)),)
