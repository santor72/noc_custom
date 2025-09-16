import json
import os
import sys
import syslog
import requests
from pprint import pprint
#import apiai
from pprint import pformat
from noc.main.models.customfieldenumgroup import CustomFieldEnumGroup
from noc.main.models.customfieldenumvalue import CustomFieldEnumValue
from noc.fm.models.activeevent import ActiveEvent
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.core.mongo.connection import connect

capikey="cateirEkGaHaichapEcsyoDribviOj"
capiurl="http://10.1.40.201:8087/api"
cheaders = {'Content-type': 'application/json', 'Authorization': "apikey " + capikey}


def aievent(event):
#    logging.info(json.dumps(dir(alarm)))
#    syslog.openlog(acility=syslog.LOCAL2)
#    syslog.syslog(syslog.LOG_INFO, json.dumps(alarm.body))
    apiaikey01 = str(CustomFieldEnumValue.objects.get(key='apiai01', enum_group=CustomFieldEnumGroup.objects.get(name='aikeys')).value)
    request = apiai.ApiAI(apiaikey01).text_request()
    request.lang = 'en'
    request.session_id = 'RNNOCAlarmAI'
    request.query = json.dumps({'mo':event.managed_object_id,'body' : event.body, 'raw' : event.raw_vars})
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
#    syslog.syslog(syslog.LOG_INFO, json.dumps(responseJson))

#Функции отправки алармов в cetnrifugo для отображения на оперативной карте
def linkopentocf(alarm):
#    ctx = {"alarm": alarm}
#    body = alarm.open_template.render_body(**ctx)
    if not 'interface' in alarm.vars:
        return 0
    connect()
    event = ActiveEvent.objects.get(id = alarm.opening_event)
    mo = alarm.managed_object
    i = Interface.objects.filter(managed_object=mo,name=alarm.vars['interface']).first()
    if i:
        ipr=i.profile
    else:
        return 0
    if ipr.status_change_notification == 'e':    
        message = {
                    "method": "publish",
                    "params": {
                        "channel": "ch_alarm",
                        "data": {
                        "msg": event.body,
                        "id": mo.address,
                        "descr": mo.description,
                        "name": mo.name, 
                        "repeats": event.repeats,
                        "subject": event.subject,
                        "ts": int(round(alarm.timestamp.timestamp())),
                        "has_alarm": 1
                        }
                }
                }
        response = requests.post(capiurl,verify=False, headers=cheaders, json=message)
        return 1
    else:
        return 0

def linkclosetocf(alarm):
    if not 'interface' in alarm.vars:
        return 0
    event = ActiveEvent.objects.get(id = alarm.opening_event)
    connect()
    mo = alarm.managed_object
    i = Interface.objects.filter(managed_object=mo,name=alarm.vars['interface']).first()
    if i:
        ipr=i.profile
    else:
        return 0
    if ipr.status_change_notification == 'e':    
        message = {
                    "method": "publish",
                    "params": {
                        "channel": "ch_alarm",
                        "data": {
                            "msg": event.body,
                            "id": mo.address,
                            "descr": mo.description,
                            "name": mo.name,
                            "repeats": event.repeats,
                            "subject": event.subject,
                            "ts": int(round(alarm.timestamp.timestamp())),
                            "has_alarm": 0
                        }
                    }
                }
        response = requests.post(capiurl,verify=False, headers=cheaders, json=message)
        return 1
    else:
        return 0

def opentocf(alarm):
#    ctx = {"alarm": alarm}
#    body = alarm.open_template.render_body(**ctx)
    connect()
    event = ActiveEvent.objects.get(id = alarm.opening_event)
    mo = alarm.managed_object
    message = {
                "method": "publish",
                "params": {
                    "channel": "ch_alarm",
                    "data": {
                        "msg": event.body,
                        "id": mo.address,
                        "descr": mo.description,
                        "name": mo.name, 
                        "repeats": event.repeats,
                        "subject": event.subject,
                        "ts": int(round(alarm.timestamp.timestamp())),
                        "has_alarm": 1
                    }
                }
            }
    response = requests.post(capiurl,verify=False, headers=cheaders, json=message)

def closetocf(alarm):
    connect()
    event = ActiveEvent.objects.get(id = alarm.closing_event)
    mo = alarm.managed_object
    message = {
                "method": "publish",
                "params": {
                    "channel": "ch_alarm",
                    "data": {
                        "msg": event.body,
                        "id": mo.address,
                        "descr": mo.description,
                        "name": mo.name, 
                        "repeats": event.repeats,
                        "subject": event.subject,
                        "ts": int(round(alarm.timestamp.timestamp())),
                        "has_alarm": 0
                    }
                }
            }
    response = requests.post(capiurl,verify=False, headers=cheaders, json=message)

def ospfopentocf(alarm):
#    ctx = {"alarm": alarm}
#    body = alarm.open_template.render_body(**ctx)
    connect()
    event = ActiveEvent.objects.get(id = alarm.opening_event)
    mo = alarm.managed_object
    message = {
                "method": "publish",
                "params": {
                    "channel": "ch_alarm",
                    "data": {
                        "msg": event.body,
                        "id": mo.address,
                        "descr": mo.description,
                        "name": mo.name,
                        "repeats": event.repeats,
                        "subject": event.subject,
                        "ts": int(round(alarm.timestamp.timestamp())),
                        "has_alarm": 1
                    }
                }
            }
    response = requests.post(capiurl,verify=False, headers=cheaders, json=message)

def ospfclosetocf(alarm):
    connect()
    event = ActiveEvent.objects.get(id = alarm.closing_event)
    mo = alarm.managed_object
    message = {
                "method": "publish",
                "params": {
                    "channel": "ch_alarm",
                    "data": {
                        "msg": event.body,
                        "id": mo.address,
                        "descr": mo.description,
                        "name": mo.name,
                        "repeats": event.repeats,
                        "subject": event.subject,
                        "ts": int(round(alarm.timestamp.timestamp())),
                        "has_alarm": 0
                    }
                }
            }
    response = requests.post(capiurl,verify=False, headers=cheaders, json=message)
