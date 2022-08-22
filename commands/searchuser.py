# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import argparse
import re
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--login", dest="login", default=None)
    def searchonbras(self,mac):
      re_pppoe_info = re.compile(r'^\s+(?P<uid>\d+)\s+.+$',
                                 re.DOTALL | re.MULTILINE | re.IGNORECASE)
      re_sub = re.compile(r'^Type:\s+PPPoE.+Identity:\s+(?P<login>\S+)\s+.+', re.DOTALL | re.MULTILINE | re.IGNORECASE)
      data1 = self.bras.scripts.commands(commands= ['show pppoe session | i {}'.format(mac)])
      m1 = re_pppoe_info.search(data1['output'][0])
      if m1:
         data2 = self.bras.scripts.commands(commands= ['show subscriber session uid {}'.format(m1.group('uid'))])
         m2 = re_sub_info.search(data2['output'][0])
         if m2:
            return m2.group('login')
         else:
            return ''

    def handle(self, *args, **options):
        connect()
        login = options.get("login")
        if login:
                    sessions=[]
                    re_session = re.compile(r"Type: PPPoE.+UID:\s+(?P<uid>\S+),.+\s+Identity:\s+(?P<login>\S+)")
                    
                    #Для всех логинов, для всех брасов формируем список комманд и выполняем их
                    from noc.sa.models.action import Action
                    from noc.sa.models.managedobject import ManagedObject
                    cmd = [f"show subscriber session username {login}"]
                    selector = ManagedObjectSelector.objects.filter(name=selector_name)
                    bras = selector[0].managed_objects
                    for i in range(len(bras)):
                        r = bras[i].scripts.commands(commands=cmd)
                        for s in r['output'][0].split('\n'):
                            m = re_session.match(s)
                            if m:
                               sessions.append({'uid': m.group('uid'), 'login': m.group('login'), 'bras': bras[i].address})
                    if sessions:
                        for item in sessions:
                            bras = ManagedObject.objects.filter(address = item['bras'])
                            r = bras[0].scripts.commands(commands=[f"show pppoe session all | i {item['uid']}"])
                            re_pppoe = re.compile("^\s+{item['uid']}\s+\S+\s+(?P<mac>\S+)\s+(?P<int>\S+)\s+")
                            for s in r['output'][0].split('\n'):
                               m = re_pppoe.match(s)
                               if m:
                                  item['mac'] = m.group('mac')
                                  item['int'] = m.group('int')

                    pprint(sessions)
        else:
            print("Need --account parametr")

if __name__ == "__main__":
    selector_name = 'bras'
    Command().run()
