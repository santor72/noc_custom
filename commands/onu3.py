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
from noc.core.mongo.connection import connect
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
        parser.add_argument("-b", "--bras", dest="bras", default=None)
    
    def handle(self, *args, **options):
        connect()
        self.olt_id = options.get("olt")
        self.fname = options.get("file")
        self.bras_id = options.get("bras")
        if (not self.olt_id):
            self.help()
            return
        self.getusdata()
        self.olt =  ManagedObject.objects.get(id=self.olt_id)
        self.bras =  ManagedObject.objects.get(id=self.bras_id)
        self.getonulist()

    def searchonbras(self,mac):
      re_pppoe_info = re.compile(r'^\s+(?P<uid>\d+)\s+.+$',
                                 re.DOTALL | re.MULTILINE | re.IGNORECASE)
      re_sub_info = re.compile(r'^Type:\s+PPPoE.+Identity:\s+(?P<login>\S+)\s+.+', re.DOTALL | re.MULTILINE | re.IGNORECASE)
      data1 = self.bras.scripts.commands(commands= ['show pppoe session | i {}'.format(mac)])
      m1 = re_pppoe_info.search(data1['output'][0])
      if m1:
         data2 = self.bras.scripts.commands(commands= ['show subscriber session uid {}'.format(m1.group('uid'))])
         m2 = re_sub_info.search(data2['output'][0])
         if m2:
            return m2.group('login')
         else:
            return ''

    def getonulist(self):
#        r = self.apiurl_rn + '&cat=usm_pon&action=list_onu&device_id={}'.format(self.olt_id)
#        response = requests.get(r,verify=True, headers=headers)
#        if (response.ok):
#            data = json.loads(response.content)
#        else:
#            response.raise_for_status()
        data_dict = {'interface' : '',
                'llid' : '',
                'sn' : '',
                'conftype' : '',
                'distance' : '',
                'lprofile' : '',
                'sprofile' : '',
                'rstate' : '',
                'state' : '',
                'version' : '',
                'model' : '',
                'oltrx' : '',
                'downatt' : '',
                'onutx' : '',
                'upatt' : '',
                'username' : '',
                'mac': '',
                'vlan': ''
        }
        action = Action.objects.get(name='showonu')
        data = self.olt.scripts.commands(commands= [str(action.expand(self.olt))])
        l = []
        rx_onu = re.compile(r'^gpon-onu_(?P<interface>\d/\d/\d):(?P<llid>\d{1,3}).+$',  re.MULTILINE | re.IGNORECASE)
        rx_onu2 = re.compile(r'^(?P<interface>\d/\d/\d):(?P<llid>\d{1,3}).+$',  re.MULTILINE | re.IGNORECASE)
        rx_onuinfo = re.compile('^.+Type:\s+(?P<conftype>\S+)\s+State:\s+(?P<state>\S+)\s.+'
                r'Phase\sstate:\s+(?P<rstate>\S+)\s.+'
                r'Serial\snumber:\s+(?P<sn>\S+)\s+.+Password.+Line\sProfile:\s+(?P<lprofile>\S+)\s+'
                r'Service\s+Profile:\s+(?P<sprofile>\S+)\s+.+ONU\s+Distance:\s+(?P<distance>\S+)\s+.+$',
                re.DOTALL | re.MULTILINE | re.IGNORECASE)

        rx_onuinfo2 = re.compile(r'^.+Version:\s+(?P<version>\S+)\s+SN.+Model:\s+(?P<model>\S+)\s+.+$',
                re.DOTALL | re.MULTILINE | re.IGNORECASE)
        rx_power2 = re.compile(r'^.+up\s+Rx\s+:(?P<otlrx>\S+)\(dbm\).+\(dbm\)\s+(?P<downatt>\S+)\(dB\).+'
                               r'down\s+Tx.+Rx:(?P<onurx>\S+)\(dbm\)\s+(?P<upatt>\S+)\(dB\).+$',
                               re.DOTALL | re.MULTILINE | re.IGNORECASE)
        rx_username = re.compile(r'^.+(?:pppoe|wan-ip).+(?:user|username)\s+(?P<username>\S+)\s+.+$',
                                 re.DOTALL | re.MULTILINE | re.IGNORECASE)
        rx_mac = re.compile(r'Mac\s+address\s+Vlan\s+Type\s+Port\s+Vc\n.+\n([a-f,0-9]+.[a-f,0-9]+.[a-f,0-9]+)\s+(\d+)\s+',
                                 re.DOTALL | re.MULTILINE | re.IGNORECASE)
        for i in data['output'][0].split('\n'):

            m = rx_onu.search(i)
            if not m:
               m = rx_onu2.search(i)
            if m:
              try:
#                print(i)
                print(m.group('interface') + ':' + m.group('llid'))
                action = Action.objects.get(name='showonuinfo')
                data2 = self.olt.scripts.commands(commands= ['sho gpon onu detail-info gpon-onu_{}:{}'.format(m.group('interface'),m.group('llid'))])
                data3 = self.olt.scripts.commands(commands= ['show pon power att gpon-onu_{}:{}'.format(m.group('interface'),m.group('llid'))])
                data4 = self.olt.scripts.commands(commands= ['sho gpon remote-onu equip gpon-onu_{}:{}'.format(m.group('interface'),m.group('llid'))])
                data5 = self.olt.scripts.commands(commands= ['sho onu run con  gpon-onu_{}:{}'.format(m.group('interface'),m.group('llid'))])
                data6 = self.olt.scripts.commands(commands= ['show mac gpon onu gpon-onu_{}:{}'.format(m.group('interface'),m.group('llid'))])
                f1 = open(self.fname + '/' + m.group('interface').replace('/','-') + '_' + m.group('llid'), 'w')
                f1.write(data2['output'][0])
                f1.write(data3['output'][0])
                f1.write(data4['output'][0])
                f1.write(data5['output'][0])
                f1.write(data6['output'][0])
                f1.close()
              except:
                continue
        return



if __name__ == "__main__":
    Command().run()
