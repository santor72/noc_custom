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
import pprint
import re
import csv
import os
import argparse
import string
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
        self.apiurl = self.url + 'key=' + self.apikey
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
        r=self.apiurl + '&cat=inventory&action=get_inventory_catalog_id_by_name&name=ZTE ZXHN F660'
        response = requests.get(r,verify=True, headers=headers)
        if (response.ok):
            data = json.loads(response.content)
        else:
            response.raise_for_status()
        if data['Result'] == 'OK':
            ztecpeid = data['id']
        else:
            ztecpeid = 0
        for item in res:
            if item['inus'] == 'N' and item['vendor'] == 'CZTE' and ztecpeid != 0:
#                r = self.apiurl + '&cat=inventory&action=add_inventory&inventory_catalog_id={}&sn={}&additional_data_mac={}'.format(ztecpeid, item['id'], item['mac'])
                r = self.apiurl + '&cat=inventory&action=add_inventory&inventory_catalog_id={}&sn={}&comment={}'.format(ztecpeid, item['id'], item['model'])
                response = requests.get(r,verify=True, headers=headers)
                if (response.ok):
                     data = json.loads(response.content)
                else:
                     response.raise_for_status()
#                print(r)
        if fname:
            with open(fname, "w") as out_file:
                writer = csv.DictWriter(out_file, delimiter=';', fieldnames = res[0].keys())
                writer.writeheader()
                for item in res:
                    writer.writerow(item)



        
    def getonulist(self):
        l = []
        r = self.apiurl_rn + '&cat=usm_pon&action=list_onu&device_id={}'.format(self.olt_id)
        response = requests.get(r,verify=True, headers=headers)
        if (response.ok):
            data = json.loads(response.content)
        else:
            response.raise_for_status()
        for items in data['onulist']:
            item = data['onulist'][items]
            if item['mac'] != '' and item['id'] == '':
                item['id'] = item['mac']
            r1 = self.apiurl + '&cat=inventory&action=get_inventory_id&data_typer=serial_number&data_value={}'.format(item['id'])
            response = requests.get(r1,verify=True, headers=headers)
            if (response.ok):
                data1 = json.loads(response.content)
            else:
                response.raise_for_status()
            if data1['Result'] == 'ERROR':
                inus = 'N'
            else:
                inus = 'Y'
            i = string.replace(string.replace(item['ifaceName'],'OLT ',''),'EPON','').split(':')
            action = Action.objects.get(name='showonuinfo')
            clidata = self.olt.scripts.commands(commands= [str(action.expand(self.olt,interface=i[0],llid=i[1]))])
            l.append({'ifaceName' : item['ifaceName'],
                'interface' : i[0],
                'llid' : i[1],
                'id' : item['id'],
                'mac' : item['mac'],
                'vendor' : item['vendor'],
                'model' : item['model'],
                'inus' : inus,
                'cli' : clidata['output'][0]
                })

        return l 



if __name__ == "__main__":
    Command().run()
