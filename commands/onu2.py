# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Zabbix Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import re
import csv
import os
import argparse

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.remotesystem import RemoteSystem
from noc.core.management.base import BaseCommand
from noc.sa.models.action import Action
import cPickle  as pickle
headers = {'Content-type': 'application/json'}

class Command(BaseCommand):
    def help(self):
        print("--olt - olt id in Userside")
        print("-f --file - outputfile")

    def getusdata(self):
        self.us = RemoteSystem.objects.get(name = 'RNUserside')
        self.url = self.us.config.get("apiurl", None)
        self.url_rn = self.us.config.get("apiurl_rn", None)
        self.apikey = self.us.config.get("apikey", None)
        self.apiurl = self.url + self.apikey
        self.apiurl_rn = self.url_rn + 'key='+ self.apikey

    def add_arguments(self, parser):
        parser.add_argument("-o", "--olt", dest="olt", default=None)
        parser.add_argument("-f", "--file", dest="file", default=None)
    
    def handle(self, *args, **options):
        self.olt_id = options.get("olt")
        fname = options.get("file")
        if (not self.olt_id):
            self.help()
            return
        self.getusdata()
        self.olt =  ManagedObject.objects.get(remote_system  = self.us, remote_id = self.olt_id)
        res = self.getonulist()
        pprint(res)
        if fname:
            with open(fname,'wb') as f:
                pickle.dump(res,f)
            f.close()

        
    def getonulist(self):
#        r = self.apiurl_rn + '&cat=usm_pon&action=list_onu&device_id={}'.format(self.olt_id)
#        response = requests.get(r,verify=True, headers=headers)
#        if (response.ok):
#            data = json.loads(response.content)
#        else:
#            response.raise_for_status()

        action = Action.objects.get(name='showonu')
        data = self.olt.scripts.commands(commands= [str(action.expand(self.olt))])
        l = []
        rx_onu = re.compile(r'^gpon-onu_(?P<interface>\d/\d/\d):(?P<llid>\d{1,3}).+$',  re.MULTILINE | re.IGNORECASE)
        rx_onuinfo = re.compile('^.+Type:\s+(?P<conftype>\S+)\s+State:\s+(?P<state>\S+)\s.+'
                r'Phase\sstate:\s+(?P<rstate>\S+)\s.+'
                r'Serial\snumber:\s+.+Line\sProfile:\s+(?P<sprofile>\S+)\s+'
                r'Service\s+Profile:\s+(?P<lprofile>\S+)\s+.+ONU\s+Distance:\s+(?P<distance>\S+)\s+.+'
                r'Version:\s+(?P<version>\S+)\s+SN.+Model:\s+(?P<model>\S+)\s+.+$',
                re.DOTALL | re.MULTILINE | re.IGNORECASE)
        for i in data['output'][0].split('\n'):
            m = rx_onu.search(i)
            if m:
#                print(i)
#                print(m.group('interface') + m.group('llid'))
                action = Action.objects.get(name='showonuinfo')
                data2 = self.olt.scripts.commands(commands= [str(action.expand(self.olt, llid=m.group('llid'),interface=m.group('interface') ))])
                m1 = rx_onuinfo.search(data2['output'][0])
                if not m1:
                    l.append({'interface' : m.group('interface'), 'llid' : m.group('llid'), 'data' : {}})
                else:
                    l.append({'interface' : m.group('interface'), 'llid' : m.group('llid'), 'data' : 
                        {'conftype' : m1.group('conftype'),
                            'distance' : m1.group('distance'),
                            'lprofile' : m1.group('lprofile'),
                            'sprofile' : m1.group('sprofile'),
                            'rstate' : m1.group('rstate'),
                            'state' : m1.group('state'),
                            'version' : m1.group('version'),
                            'model' : m1.group('model')
                            }
                        })
        return l



if __name__ == "__main__":
    Command().run()
