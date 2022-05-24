# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import argparse
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--login", dest="login", default=None)

    def handle(self, *args, **options):
        connect()
        login = 'aaa'
        output=[]
        if login:
                    from noc.sa.models.action import Action
                    from noc.sa.models.managedobject import ManagedObject
                    data = {'host': '10.6.6.40', 'llid': 1, 'login': '16532', 'passwd': '2za9d2s8', 'port': '1/1/8', 'sn': 'ZTEGC101F4B6', 'vlanid': 1301}
                    mo = ManagedObject.objects.get(address = data['host'])
                    action = Action.objects.get(name='zteunregonu')
                    cmd1 = str(action.expand(mo,**data))
                    params={"commands":cmd1.split('\n'), "ignore_cli_errors":True}
                    result = mo.scripts.commands(**params)
                    output.append(result)
                    action = Action.objects.get(name='f620-router')
                    cmd2 = str(action.expand(mo,**data))
                    print(cmd2.split('\n'))
#                    return 1
                    params={"commands":cmd2.split('\n'), "ignore_cli_errors":True}
                    result = mo.scripts.commands(**params)
                    output.append(result)
                    action = Action.objects.get(name='zteconfpppoe')
                    cmd21 = str(action.expand(mo,**data))
                    print(cmd21.split('\n'))
#                    return 1
                    params={"commands":cmd21.split('\n'), "ignore_cli_errors":True}
                    result = mo.scripts.commands(**params)
#                    action = Action.objects.get(name='ztewrite')
#                    com3 = str(action.expand(mo))
                    result = mo.scripts.commands(commands = ['write'])
                    output.append(result)
                    return 200, [output]

if __name__ == "__main__":
    Command().run()
