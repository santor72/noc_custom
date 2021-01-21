# coding: utf-8
import sys
from pathlib import Path
cwd = '/opt/noc_custom/lib'
sys.path.insert(0, cwd)
from helper import *
import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import argparse
from noc.core.management.base import BaseCommand
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.remotesystem import RemoteSystem

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--login", dest="login", default=None)

    def handle(self, *args, **options):
        from noc.core.mongo.connection import connect
        connect()
        us = RemoteSystem.objects.get(name = 'RNUserside')
        apikey = us.config.get("apikey", None)
        apiurl = us.config.get("apiurl", None)
        usurl=apiurl+'key='+apikey
        login = options.get("login")
        if login:
             customer_id=getcustomer(usurl,login)
             if customer_id:
                devices=getdevices(usurl,customer_id)
                action = Action.objects.get(name='disable_interface')
                for device in devices:
                   mo = ManagedObject.objects.get(address=device['host'])
                   commands = [str(action.expand(mo,interface=device['ifname']))]
                   r = mo.scripts.commands(commands=commands)
                   pprint(r)
        else:
            print("Need --account parametr")

if __name__ == "__main__":
    Command().run()
