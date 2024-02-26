import json
import os
import sys
import syslog
import requests
from pprint import pprint
import apiai
from pprint import pformat
from noc.main.models.customfieldenumgroup import CustomFieldEnumGroup
from noc.main.models.customfieldenumvalue import CustomFieldEnumValue

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
    
def opentocf(event):
    a=1
    message = {
                "method": "publish",
                "params": {
                    "channel": "ch_alarm",
                    "data": {
                       "msg": pformat(event.body) + pformat(event.raw_vars),
                       "id": 1,
                       "is_onpen": 0
                    }
               }
            }
def closetocf(event):
    message = {
                "method": "publish",
                "params": {
                    "channel": "ch_alarm",
                    "data": {
                       "msg": pformat(event.body) + pformat(event.raw_vars),
                       "id": 1,
                       "is_clear": 1
                    }
               }
            }    

