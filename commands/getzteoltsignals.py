# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
import re
from pprint import pprint
import argparse
from utm5 import UTM5
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="fname", default=None)
        parser.add_argument("-o", "--olt", dest="olt", default=None)

    def handle(self, *args, **options):
        connect()
        fname = options.get("fname")
        olt = options.get("olt")
        if fname and olt:
            from noc.sa.models.action import Action
            from noc.sa.models.managedobject import ManagedObject
            olt = ManagedObject.objects.get(id=olt)
            with open(fname, "r") as read_file:
                data = json.load(read_file)
            out = open(fname+'.csv','w')
            for item in data:
                up ='n'
                down = 'n'
                command = [str('show pon power attenuation  gpon-onu_'+item['interface']+':'+item['id'])]
                r = olt.scripts.commands(commands=command)
                for i in r['output'][0].split('\n'):
                    if re.match(r'^\s+up\s+Rx\s+:(?P<otltrx>\S+)\s+', i):
                        up = re.match(r'^\s+up\s+Rx\s+:(?P<otltrx>\S+)\s+', i).group(1)
                    if re.match(r'^\s+down\s+Tx\s+:(?P<onutx>\S+)\s+.+:(?P<onurx>\S+)\s+', i):
                        down = re.match(r'^\s+down\s+Tx\s+:(?P<onutx>\S+)\s+.+:(?P<onurx>\S+)\s+', i).group(2)
                print(item['interface']+'\t'+item['id'])
                out.write(item['interface']+'\t'+item['id']+'\t'+item['sn']+'\t'+item['login']+'\t'+up+'\t'+down+'\n')
            close(out)
#                downlevel = re.match(r'^\s+down\s+Rx\s+:(?P<onurx>\S+)\s+', i)
#            print(str(r['output'][0]))
#            if uplevel:
#               up = uplevel.group(0)
#            if downlevel:
#               down = downlevel.group(0)

            
        else:
            print("Need --file and --olt parametr")

if __name__ == "__main__":
    Command().run()

