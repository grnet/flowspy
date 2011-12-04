from utils import proxy as PR
from celery.task import task
from celery.task.sets import subtask
import logging
import json

from celery.task.http import *
from flowspy.utils import beanstalkc
from django.conf import settings

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@task
def add(route, callback=None):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply()
    if commit:
        status = "ACTIVE"
    else:
        status = "ERROR"
    route.status = status
    route.response = response
    subtask(announce).delay("[%s] Route add: %s - Result: %s" %(route.applier, route.name, response), route.applier)
    route.save()

@task
def edit(route, callback=None):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply(operation="replace")
    if commit:
        status = "ACTIVE"
    else:
        status = "ERROR"
    route.status = status
    route.response = response
    route.save()
    subtask(announce).delay("[%s] Route edit: %s - Result: %s"%(route.applier, route.name, response), route.applier)



@task
def delete(route, callback=None):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply(operation="delete")
    if commit:
        status = "INACTIVE"
    else:
        status = "ERROR"
    route.status = status
    route.response = response
    route.save()
    subtask(announce).delay("[%s] Route delete: %s - Result %s" %(route.applier, route.name, response), route.applier)



@task
def announce(messg, user):
    messg = str(messg)
#    username = user.username
    username = user.get_profile().peer.domain_name
    b = beanstalkc.Connection()
    b.use(settings.POLLS_TUBE)
    tube_message = json.dumps({'message': messg, 'username':username})
    b.put(tube_message)
    b.close()

@task
def check_sync(route_name=None, selected_routes = []):
    if not selected_routes:
        routes = Route.objects.all()
    else:
        routes = selected_routes
    if route_name:
        routes = routes.filter(name=route_name)
    for route in roures:
        if route.is_synced():
            logger.info("Route %s is synced" %route.name)
        else:
            logger.warn("Route %s is out of sync" %route.name)
#def delete(route):
#    
#    applier = PR.Applier(route_object=route)
#    commit, response = applier.apply(configuration=applier.delete_routes())
#    if commit:
#            rows = queryset.update(is_online=False, is_active=False)
#            queryset.update(response="Successfully removed route from network")
#            self.message_user(request, "Successfully removed %s routes from network" % rows)
#        else:
#            self.message_user(request, "Could not remove routes from network")
#    if commit:
#        is_online = False
#        is_active = False
#        response = "Successfully removed route from network"
#    else:
#        is_online = False
#        is_active = True
#    route.is_online = is_online
#    route.is_active = is_active
#    route.response = response
#    route.save()