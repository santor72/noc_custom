# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
import re
from pprint import pprint
import argparse
import time
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--login", dest="login", default=None)

    def handle(self, *args, **options):
        connect()
        from noc.sa.models.action import Action
        from noc.sa.models.managedobject import ManagedObject
        from noc.fm.models.activeevent import ActiveEvent
        from noc.fm.models.eventclass import EventClass
        from noc.fm.models.eventlog import EventLog
        rx_statestr = re.compile('^gpon-onu_1\/1\/9:7\s+(?P<AdminState>\S+)\s+(?P<OMCCState>\S+)\s+(?P<O7State>\S+)\s+(?P<PhaseState>\S+)\s+$')
        action = Action.objects.get(name='showonuinfo')
#                    bras = [ManagedObject.objects.get(id=105), ManagedObject.objects.get(id=86), ManagedObject.objects.get(id=360)]
        olt = [ManagedObject.objects.get(id=361)]
#        s = olt[0].scripts.commands(commands="show gpon onu state gpon-olt_1/1/9")
        commands = [str(action.expand(olt[0],interface='1/1/9', llid=x))  for x in [7]] 
#        print(commands)
        s = olt[0].scripts.commands(commands=commands)
        s1 = s['output'][0].split('\n')
        for i in range(len(s1)):
            if rx_statestr.match(s1[i]):
               r = rx_statestr.search(s1[i])
               if (r.group('O7State') != 'operation' or r.group('PhaseState') != 'orking'):
                   print('raise')
                   ac = EventClass.objects.get(id='5c49700b94c61c465e031c9e')
                   #print(olt[0].id)
                   a = ActiveEvent(
                     timestamp = time.time(),
                     managed_object = olt[0].id,
                     event_class = ac.id,
                     start_timestamp  = time.time(),
                     repeats = 0,
                     log=[
                        EventLog(
                          message='Talej may have power error. Test ONU state no in [operation,working]'
                        )
                     ]
                   )
                   print(a)
                   a.save()

if __name__ == "__main__":
    Command().run()
