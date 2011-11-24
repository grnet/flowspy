from utils import proxy as PR
from celery.task import task
from celery.task.sets import subtask
import logging
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
        is_online = True
        is_active = True
    else:
        is_online = False
        is_active = True
    route.is_online = is_online
    route.is_active = is_active
    route.response = response
    subtask(announce).delay("Route add: %s - Result: %s" %(route.name, response))
    route.save()

@task
def edit(route, callback=None):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply(operation="replace")
    if commit:
        is_online = True
    else:
        is_online = False
    route.is_active = True
    route.is_online = is_online
    route.response = response
    route.save()
    subtask(announce).delay("Route edit: %s - Result: %s" %(route.name, response))



@task
def delete(route, callback=None):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply(operation="delete")
    if commit:
        is_online = False
        is_active = False
    else:
        is_online = route.is_online
        is_active = route.is_active
    route.is_online = is_online
    route.is_active = is_active
    route.response = response
    route.save()
    subtask(announce).delay("Route delete: %s - Result %s" %(route.name, response))



@task
def announce(messg):
    messg = str(messg)
    b = beanstalkc.Connection()
    b.use(settings.POLLS_TUBE)
    b.put(messg)
    b.close()


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