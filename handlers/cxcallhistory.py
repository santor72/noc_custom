# ----------[32;39;5M-----------------------------------------------------------
# 3CX.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
#curl -XPOST 'http://10.1.40.201:8086/query' --data-urlencode 'q=CREATE DATABASE "ponsignals"'

# Python modules
import re
import datetime
import orjson
import requests

from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.custom.lib.cx import obj3CX
from noc.core.comp import smart_text
from noc.core.nsq.topic import TopicQueue

def yhistory(*args, **kwargs):
    url_string = 'http://10.1.40.201:8086/write?db=cc'
    ts = int((datetime.datetime.now()).timestamp())
    c_count = {}
    result = []
    connect()
    q = ManagedObject.objects.filter(name="callcenter-PBX")
    if not q:
       raise "error get MO"
    if not q[0].object_profile.name == 'Linux Server 3CX':
       raise "MO is not 3CX server"
    mo = q[0]
    cxuser = mo.get_attr('apiuser')
    cxpasswd = mo.get_attr('apipasswd')
    cxurl = mo.get_attr('apiurl')
    cx = obj3CX(user=cxuser,passwd=cxpasswd, url=cxurl)
    cx.login()
    try:
      result_answered = cx.calls_logs('Yesterday', 'OnlyAnswered')
      result_unanswered = cx.calls_logs('Yesterday', 'OnlyUnanswered')
      if not result_answered['failed']:
          answered=result_answered['result']
      else:
          raise "answered call get fail"
      if not result_unanswered['failed']:
          unanswered=result_unanswered['result']
      else:
          raise "unanswered call get fail"
      print(len(answered))
      print(len(unanswered))

      for item in answered:
        if not item['Destination'].find('IVR '):
           continue
        if item['ts'] in c_count.keys():
           c_count[item['ts']]['a'] = c_count[item['ts']]['a'] + 1 
        else: 
           c_count[item['ts']] = {}
           c_count[item['ts']]['a'] = 1
           c_count[item['ts']]['u'] = 0
      for item in unanswered:
        if not item['Destination'].find('IVR '):
           continue
        if item['ts'] in c_count.keys():
          c_count[item['ts']]['u'] = c_count[item['ts']]['u'] + 1
        else:
          c_count[item['ts']] = {}
          c_count[item['ts']]['u'] = 1
          c_count[item['ts']]['a'] = 0
      result = ['object']
      for k,v in c_count.items():
        dt_object = datetime.datetime.fromtimestamp(k)
        m = [{
           "measurement": "sip_calls",
           "time":  dt_object.__format__('%Y-%m-%d %H:%M:00'),
           "fields": {
               "a": v['a'],
               "u": v['u']
           }
        }]
        s = 'sipcalls,host=cc3cx,what=answeredcalls value={} {}000000000'.format(v['a'], k)
        r = requests.post(url_string, verify=False, data=s)
        s = 'sipcalls,host=cc3cx,what=unansweredcalls value={} {}000000000'.format(v['u'], k)
        r = requests.post(url_string, verify=False,  data=s)
        jm = smart_text(orjson.dumps(m))
        result += [jm]
#      if len(result) > 1:
#         topic='chwriter'
#         q = TopicQueue(topic)
#         q.put(result)
    finally:
      cx.logout()
#      return result



if __name__ == "__main__":
    yhistory()
    