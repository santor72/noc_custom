# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
import re
from pprint import pprint
import argparse
import time
import syslog
import logging
import logging.handlers
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from bson import ObjectId
import socket
import argparse

FACILITY = {
    'kern': 0, 'user': 1, 'mail': 2, 'daemon': 3,
    'auth': 4, 'syslog': 5, 'lpr': 6, 'news': 7,
    'uucp': 8, 'cron': 9, 'authpriv': 10, 'ftp': 11,
    'local0': 16, 'local1': 17, 'local2': 18, 'local3': 19,
    'local4': 20, 'local5': 21, 'local6': 22, 'local7': 23,
}

LEVEL = {
    'emerg': 0, 'alert':1, 'crit': 2, 'err': 3,
    'warning': 4, 'notice': 5, 'info': 6, 'debug': 7
}

def syslogsend(message, level=LEVEL['notice'], facility=FACILITY['daemon'],
    host='localhost', port=1514):
    """
    Send syslog UDP packet to given host and port.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = '<%d>%s' % (level + facility*8, message)
    sock.sendto(data, (host, port))
    sock.close()


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
        my_logger = logging.getLogger('MyLogger')
        rx_statestr = re.compile('^gpon-onu_1\/1\/6:13\s+(?P<AdminState>\S+)\s+(?P<OMCCState>\S+)\s+(?P<O7State>\S+)\s+(?P<PhaseState>\S+)\s+$')
        action = Action.objects.get(name='showonuinfo')
        olt = [ManagedObject.objects.get(id=361)]
        commands = [str(action.expand(olt[0],interface='1/1/6', llid=x))  for x in [13]] 
	my_logger.info('Onu on 1/1/6:13 offline. May be power loss')
#	syslogsend('Onu on 1/1/6:13 offline. May be power loss', 1, 18)
	syslogsend('Onu on 1/1/6:13 offline. May be power loss', 1, 18)
	return
        s = olt[0].scripts.commands(commands=commands)
        s1 = s['output'][0].split('\n')
#        print(s1);
        for i in range(len(s1)):
            if rx_statestr.match(s1[i]):
               r = rx_statestr.search(s1[i])
               print(r.group('O7State') + '\t' +  r.group('PhaseState'))
               if (r.group('O7State') != 'operation' or r.group('PhaseState') != 'orking'):
                   print('raise')
                   ac = EventClass.objects.get(id='5c49700b94c61c465e031c9e')
                   a = ActiveEvent(
                     id = ObjectId(),
                     source = 'Script',
                     timestamp = time.time(),
                     managed_object = olt[0].id,
                     event_class = ac.id,
                     start_timestamp  = time.time(),
                     repeats = 0,
                     log=[
                       EventLog(
                          timestamp = time.time(),
                          message='Talej may have power error. Test ONU state no in [operation,working]'
                        )
                     ]
                   )
                   a.save()
                   print(a)

if __name__ == "__main__":
    Command().run()
