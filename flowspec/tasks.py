from utils import proxy as PR
from celery.task import task

@task
def add(route):
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
    route.save()
#
#@task
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