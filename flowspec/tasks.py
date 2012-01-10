from utils import proxy as PR
from celery.task import task
from celery.task.sets import subtask
import logging
import json
from celery.task.http import *
from flowspy.utils import beanstalkc
from django.conf import settings
import datetime

import os



LOG_FILENAME = os.path.join(settings.LOG_FILE_LOCATION, 'celery_jobs.log')

#FORMAT = '%(asctime)s %(levelname)s: %(message)s'
#logging.basicConfig(format=FORMAT)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(formatter)
logger.addHandler(handler)


@task(ignore_result=True)
def add(route, callback=None):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply()
    if commit:
        status = "ACTIVE"
    else:
        status = "ERROR"
    route.status = status
    route.response = response
    route.save()
    announce("[%s] Rule add: %s - Result: %s" %(route.applier, route.name, response), route.applier)

@task(ignore_result=True)
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
    announce("[%s] Rule edit: %s - Result: %s"%(route.applier, route.name, response), route.applier)



@task(ignore_result=True)
def delete(route, **kwargs):
    applier = PR.Applier(route_object=route)
    commit, response = applier.apply(operation="delete")
    reason_text = ''
    if commit:
        status = "INACTIVE"
        if "reason" in kwargs and kwargs['reason']=='EXPIRED':
            status = 'EXPIRED'
            reason_text = " Reason: %s " %status
    else:
        status = "ERROR"
    route.status = status
    route.response = response
    route.save()
    announce("[%s] Suspending rule : %s%s- Result %s" %(route.applier, route.name, reason_text, response), route.applier)

# May not work in the first place... proxy is not aware of Route models
@task
def batch_delete(routes, **kwargs):
    if routes:
        for route in routes:
            route.status='PENDING';route.save()
        applier = PR.Applier(route_objects=routes)
        conf = applier.delete_routes()
        commit, response = applier.apply(configuration = conf)
        reason_text = ''
        if commit:
            status = "INACTIVE"
            if "reason" in kwargs and kwargs['reason']=='EXPIRED':
                status = 'EXPIRED'
                reason_text = " Reason: %s " %status
            elif "reason" in kwargs and kwargs['reason']!='EXPIRED':
                status = kwargs['reason']
                reason_text = " Reason: %s " %status
        else:
            status = "ERROR"
        for route in routes:
            route.status = status
            route.response = response
            route.expires = datetime.date.today()
            route.save()
            announce("[%s] Rule removal: %s%s- Result %s" %(route.applier, route.name, reason_text, response), route.applier)
    else:
        return False

#@task(ignore_result=True)
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
    from flowspy.flowspec.models import Route, MatchPort, MatchDscp, ThenAction
    if not selected_routes:
        routes = Route.objects.all()
    else:
        routes = selected_routes
    if route_name:
        routes = routes.filter(name=route_name)
    for route in routes:
        if route.has_expired() and (route.status != 'EXPIRED' and route.status != 'ADMININACTIVE' and route.status != 'INACTIVE'):
            logger.info('Expiring route %s' %route.name)
            subtask(delete).delay(route, reason="EXPIRED")
#        elif route.has_expired() and (route.status == 'ADMININACTIVE' or route.status == 'INACTIVE'):
#            route.status = 'EXPIRED'
#            route.response = 'Rule Expired'
#            logger.info('Expiring route %s' %route.name)
#            route.save()
        else:
            if route.status != 'EXPIRED':
                route.check_sync()


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