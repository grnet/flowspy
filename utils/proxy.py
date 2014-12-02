# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright (C) 2010-2014 GRNET S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import nxpy as np
from ncclient import manager
from ncclient.transport.errors import AuthenticationError, SSHError
from lxml import etree as ET
from django.conf import settings
import logging
from django.core.cache import cache
import os
from celery.exceptions import TimeLimitExceeded, SoftTimeLimitExceeded

cwd = os.getcwd()
    

LOG_FILENAME = os.path.join(settings.LOG_FILE_LOCATION, 'celery_jobs.log')

#FORMAT = '%(asctime)s %(levelname)s: %(message)s'
#logging.basicConfig(format=FORMAT)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(LOG_FILENAME)
handler.setFormatter(formatter)
logger.addHandler(handler)

def fod_unknown_host_cb(host, fingerprint):
    return True

class Retriever(object):
    def __init__(self, device=settings.NETCONF_DEVICE, username=settings.NETCONF_USER, password=settings.NETCONF_PASS, filter=settings.ROUTES_FILTER, port=settings.NETCONF_PORT, route_name=None, xml=None):
        self.device = device
        self.username = username
        self.password = password
        self.port = port
        self.filter = filter
        self.xml = xml
        if route_name:
            self.filter = settings.ROUTE_FILTER%route_name
    
    def fetch_xml(self):
        with manager.connect(host=self.device, port=self.port, username=self.username, password=self.password, hostkey_verify=False) as m:
            xmlconfig = m.get_config(source='running', filter=('subtree',self.filter)).data_xml
        return xmlconfig
    
    def proccess_xml(self):
        if self.xml:
            xmlconfig = self.xml
        else:
            xmlconfig = self.fetch_xml()
        parser = np.Parser()
        parser.confile = xmlconfig
        device = parser.export()
        return device    
    
    def fetch_device(self):
        device = cache.get("device")
        logger.info("[CACHE] hit! got device")
        if device:
            return device
        else:
            device = self.proccess_xml()
            if device.routing_options:
                cache.set("device", device, 3600)
                logger.info("[CACHE] miss, setting device")
                return device
            else:
                return False

class Applier(object):
    def __init__(self, route_objects = [], route_object=None, device=settings.NETCONF_DEVICE, username=settings.NETCONF_USER, password=settings.NETCONF_PASS, port=settings.NETCONF_PORT):
        self.route_object = route_object
        self.route_objects = route_objects
        self.device = device
        self.username = username
        self.password = password
        self.port = port
    
    def to_xml(self, operation=None):
        logger.info("Operation: %s"%operation)
        if self.route_object:
            logger.info("Generating XML config")
            route_obj = self.route_object
            device = np.Device()
            flow = np.Flow()
            route = np.Route()
            flow.routes.append(route)
            device.routing_options.append(flow)
            route.name = route_obj.name
            if operation == "delete":
                logger.info("Requesting a delete operation")
                route.operation = operation
                device = device.export(netconf_config=True)
                return ET.tostring(device)
            if route_obj.source:
                route.match['source'].append(route_obj.source)
            if route_obj.destination:
                route.match['destination'].append(route_obj.destination)
            try:
                if route_obj.protocol:
                    for protocol in route_obj.protocol.all():
                        route.match['protocol'].append(protocol.protocol)
            except:
                pass
            try:
                if route_obj.port:
                    for port in route_obj.port.all():
                        route.match['port'].append(port.port)
            except:
                pass
            try:
                if route_obj.destinationport:
                    for port in route_obj.destinationport.all():
                        route.match['destination-port'].append(port.port)
            except:
                pass
            try:
                if route_obj.sourceport:
                    for port in route_obj.sourceport.all():
                        route.match['source-port'].append(port.port)
            except:
                pass
            if route_obj.icmpcode:
                route.match['icmp-code'].append(route_obj.icmpcode)
            if route_obj.icmptype:
                route.match['icmp-type'].append(route_obj.icmptype)
            if route_obj.tcpflag:
                route.match['tcp-flags'].append(route_obj.tcpflag)
            try:
                if route_obj.dscp:
                    for dscp in route_obj.dscp.all():
                        route.match['dscp'].append(dscp.dscp)
            except:
                pass
            
            try:
                if route_obj.fragmenttype:
                    for frag in route_obj.fragmenttype.all():
                        route.match['fragment'].append(frag.fragmenttype)
            except:
                pass
            
            for thenaction in route_obj.then.all():
                if thenaction.action_value:
                    route.then[thenaction.action] = thenaction.action_value
                else:
                    route.then[thenaction.action] = True
            if operation == "replace":
                logger.info("Requesting a replace operation")
                route.operation = operation
            device = device.export(netconf_config=True)
            return ET.tostring(device)
        else:
            return False

    def delete_routes(self):
        if self.route_objects:
            logger.info("Generating XML config")
            device = np.Device()
            flow = np.Flow()
            for route_object in self.route_objects:
                route_obj = route_object
                route = np.Route()
                flow.routes.append(route)
                route.name = route_obj.name
                route.operation = 'delete'
            device.routing_options.append(flow)
            device = device.export(netconf_config=True)
            return ET.tostring(device)
        else:
            return False    
    
    def apply(self, configuration = None, operation=None):
        reason = None
        if not configuration:
            configuration = self.to_xml(operation=operation)
        edit_is_successful = False
        commit_confirmed_is_successful = False
        commit_is_successful = False
        if configuration:
            with manager.connect(host=self.device, port=self.port, username=self.username, password=self.password, hostkey_verify=False) as m:
                assert(":candidate" in m.server_capabilities)
                with m.locked(target='candidate'):
                    m.discard_changes()
                    try:
                        edit_response = m.edit_config(target='candidate', config=configuration, test_option='test-then-set')
                        edit_is_successful, reason = is_successful(edit_response)
                        logger.info("Successfully edited @ %s" % self.device)
                        if not edit_is_successful:
                            raise Exception()
                    except SoftTimeLimitExceeded:
                        cause="Task timeout"
                        logger.error(cause)
                        return False, cause
                    except TimeLimitExceeded:
                        cause="Task timeout"
                        logger.error(cause)
                        return False, cause
                    except Exception as e:
                        cause="Caught edit exception: %s %s" %(e,reason)
                        cause=cause.replace('\n', '')
                        logger.error(cause)
                        m.discard_changes()
                        return False, cause
                    if edit_is_successful:
                        try:
                            commit_confirmed_response = m.commit(confirmed=True, timeout=settings.COMMIT_CONFIRMED_TIMEOUT)
                            commit_confirmed_is_successful, reason = is_successful(commit_confirmed_response)
                                
                            if not commit_confirmed_is_successful:
                                raise Exception()
                            else:
                                logger.info("Successfully confirmed committed @ %s" % self.device)
                                if not settings.COMMIT:
                                    return True, "Successfully confirmed committed"
                        except SoftTimeLimitExceeded:
                            cause="Task timeout"
                            logger.error(cause)
                            return False, cause
                        except TimeLimitExceeded:
                            cause="Task timeout"
                            logger.error(cause)
                            return False, cause
                        except Exception as e:
                            cause="Caught commit confirmed exception: %s %s" %(e,reason)
                            cause=cause.replace('\n', '')
                            logger.error(cause)
                            return False, cause
                        
                        if settings.COMMIT:
                            if edit_is_successful and commit_confirmed_is_successful:
                                try:
                                    commit_response = m.commit(confirmed=False)
                                    commit_is_successful, reason = is_successful(commit_response)
                                    logger.info("Successfully committed @ %s" % self.device)
                                    newconfig = m.get_config(source='running', filter=('subtree',settings.ROUTES_FILTER)).data_xml
                                    retrieve = Retriever(xml=newconfig)
                                    logger.info("[CACHE] caching device configuration")
                                    cache.set("device", retrieve.proccess_xml(), 3600)
                                    
                                    if not commit_is_successful:
                                        raise Exception()
                                    else:
                                        logger.info("Successfully cached device configuration")
                                        return True, "Successfully committed"
                                except SoftTimeLimitExceeded:
                                    cause="Task timeout"
                                    logger.error(cause)
                                    return False, cause
                                except TimeLimitExceeded:
                                    cause="Task timeout"
                                    logger.error(cause)
                                    return False, cause
                                except Exception as e:
                                    cause="Caught commit exception: %s %s" %(e,reason)
                                    cause=cause.replace('\n', '')
                                    logger.error(cause)
                                    return False, cause
        else:
            return False, "No configuration was supplied"
            
def is_successful(response):
    from StringIO import StringIO
    doc = parsexml_(StringIO(response))
    rootNode = doc.getroot()
    success_list = rootNode.xpath("//*[local-name()='ok']")
    if len(success_list)>0:
        return True, None
    else:
        reason_return = ''
        reason_list = rootNode.xpath("//*[local-name()='error-message']")
        for reason in reason_list:
            reason_return = "%s %s" %(reason_return, reason.text)  
        return False, reason_return
    
    
def parsexml_(*args, **kwargs):
    if 'parser' not in kwargs:
        kwargs['parser'] = ET.ETCompatXMLParser()
    doc = ET.parse(*args, **kwargs)
    return doc

