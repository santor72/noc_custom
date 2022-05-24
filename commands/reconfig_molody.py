# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
import re
import sys
from pprint import pprint
import argparse
from utm5 import UTM5
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-p", "--path", dest="path", default=None)

#    def handle(self, *args, **options):
#            connect()
#        try:
#            self._handle(*args, **options)
#        except SystemExit:
#            pass
#        except Exception:
#            error_report()

    def _usage(self):
        print("Usage:")
        print("-p|--path Path variant")
        print("1 - ChPK-1 <-> Voshod <-> Molody")
        print("2 - Chpk1 - II - Molody")
        print("3 - Chpk - MPSL - Skl104 - II - Molody")
        sys.exit(1)
        
    def pathMain(self):
        print("Return Molody to main link")
        beaver = (ManagedObject.objects.filter(address="10.76.33.89"))[0]
        chpk_hw = (ManagedObject.objects.filter(address="217.76.46.109"))[0]
        skl1047600 = (ManagedObject.objects.filter(address="217.76.46.129"))[0]
        command_beaver_down = [str('conf t'),
                               str('Interface Ethernet1/0/28'),
                               str('switchport hybrid allowed vlan rem 1222 tag'),
                               #str('switchport hybrid allowed vlan rem 1227 tag'),
                               #str('switchport hybrid allowed vlan rem 1228 tag'),
                               str('Interface Ethernet1/0/27'),
                               str('switchport hybrid allowed vlan rem 1222 tag'),
                               str('end'),
                               str('write'),
                               str('Y')
                              ]
        command_beaver_up = [str('conf t'),
                               str('Interface Ethernet1/0/7'),
                               str('switchport hybrid allowed vlan rem 1222 tag'),
                               str('switchport hybrid allowed vlan rem 160 tag'),
                               str('switchport hybrid allowed vlan rem 423 tag'),
                               str('switchport hybrid allowed vlan rem 3250 tag'),
                               str('end'),
                               str('write'),
                               str('Y')
                              ]
        command_chpkhw = [str(),
                               str('system-view'),
                               str('interface XGigabitEthernet0/0/21'),
                               str('undo port hybrid tagged vlan 3250'),
                               str('interface XGigabitEthernet0/0/17'),
                               str('undo port hybrid tagged vlan 1222'),
                               str('undo port hybrid tagged vlan 1227'),
                               str('undo port hybrid tagged vlan 1228'),
                               str('interface XGigabitEthernet0/0/16'),
                               str('port hybrid tagged vlan 1222'),
                               str('port hybrid tagged vlan 160'),
                               str('port hybrid tagged vlan 3250'),
                               str('port hybrid tagged vlan 1227'),
                               str('port hybrid tagged vlan 1228'),
                               str('port hybrid tagged vlan 423'),
                               str('quit'),
                               str('quit'),
                               str('save all'),
                               str('Y')
                              ]
        command_skl104_down = [str('conf t'),
                               str('Interface GigabitEthernet3/9.1222'),
                               str('shutdown'),
                               str('end'),
                               str('write')
                              ]
        pprint(command_beaver_down)
        pprint(command_chpkhw)
        pprint(command_skl104_down)
#        return 0
        r1 = beaver.scripts.commands(commands=command_beaver_down)
        r2 = skl1047600.scripts.commands(commands=command_skl104_down)
        r3 = chpk_hw.scripts.commands(commands=command_chpkhw)
        r1 = beaver.scripts.commands(commands=command_beaver_up)
        pprint(r1)
        pprint(r2)
        pprint(r3)

    def pathReserv(self):
        beaver = (ManagedObject.objects.filter(address="10.76.33.89"))[0]
        chpk_hw = (ManagedObject.objects.filter(address="217.76.46.109"))[0]
        skl1047600 = (ManagedObject.objects.filter(address="217.76.46.129"))[0]
        command_beaver = [str('conf t'),
                               str('Interface Ethernet1/0/27'),
                               str('switchport hybrid allowed vlan rem 1222 tag'),
                               str('switchport hybrid allowed vlan rem 1227 tag'),
                               str('switchport hybrid allowed vlan rem 1282 tag'),
                               str('Interface Ethernet1/0/7'),
                               str('switchport hybrid allowed vlan add 1222 tag'),
                               str('switchport hybrid allowed vlan add 160 tag'),
                               str('switchport hybrid allowed vlan add 423 tag'),
                               str('switchport hybrid allowed vlan add 3250 tag'),
                               str('switchport hybrid allowed vlan add 1227 tag'),
                               str('switchport hybrid allowed vlan add 1228 tag'),
                               str('Interface Ethernet1/0/28'),
                               str('switchport hybrid allowed vlan add 1222 tag'),
                               str('switchport hybrid allowed vlan add 1227 tag'),
                               str('switchport hybrid allowed vlan add 1228 tag'),
                               str('end'),
                               str('write'),
                               str('Y')
                        ]
        command_chpkhw = [str(),
                               str('system-view'),
                               str('interface XGigabitEthernet0/0/16'),
                               str('undo port hybrid tagged vlan 1222'),
                               str('undo port hybrid tagged vlan 160'),
                               str('undo port hybrid tagged vlan 3250'),
                               str('undo port hybrid tagged vlan 1227'),
                               str('undo port hybrid tagged vlan 1228'),
                               str('undo port hybrid tagged vlan 423'),
                               str('interface XGigabitEthernet0/0/21'),
                               str('port hybrid tagged vlan 3250'),
                               str('interface XGigabitEthernet0/0/17'),
                               str('port hybrid tagged vlan 1222'),
                               str('port hybrid tagged vlan 1227'),
                               str('port hybrid tagged vlan 1228'),
                               str('quit'),
                               str('quit'),
                               str('save all'),
                               str('Y')
                              ]
        command_skl104 = [str('conf t'),
                               str('Interface GigabitEthernet3/9.1222'),
                               str('shutdown'),
                               str('end'),
                               str('write')
                              ]
        pprint(command_beaver)
        pprint(command_chpkhw)
        pprint(command_skl104)
#        return 0
        r3 = chpk_hw.scripts.commands(commands=command_chpkhw)
        r1 = beaver.scripts.commands(commands=command_beaver)
        r2 = skl1047600.scripts.commands(commands=command_skl104)
        pprint(r1)
        pprint(r2)
        pprint(r3)

    def pathSklady(self):
        beaver = (ManagedObject.objects.filter(address="10.76.33.89"))[0]
        chpk_hw = (ManagedObject.objects.filter(address="217.76.46.109"))[0]
        skl1047600 = (ManagedObject.objects.filter(address="217.76.46.129"))[0]
        command_beaver = [str('conf t'),
                               str('Interface Ethernet1/0/28'),
                               str('switchport hybrid allowed vlan rem 1222 tag'),
                               #str('switchport hybrid allowed vlan rem 1227 tag'),
                               #str('switchport hybrid allowed vlan rem 1228 tag'),
                               str('Interface Ethernet1/0/7'),
                               str('switchport hybrid allowed vlan add 1222 tag'),
                               str('switchport hybrid allowed vlan add 160 tag'),
                               str('switchport hybrid allowed vlan add 423 tag'),
                               str('switchport hybrid allowed vlan add 3250 tag'),
                               #str('switchport hybrid allowed vlan add 1227 tag'),
                               #str('switchport hybrid allowed vlan add 1228 tag'),
                               str('Interface Ethernet1/0/27'),
                               str('switchport hybrid allowed vlan add 1222 tag'),
                               #str('switchport hybrid allowed vlan add 1227 tag'),
                               #str('switchport hybrid allowed vlan add 1228 tag'),
                               str('end'),
                               str('write'),
                               str('Y')
                        ]
        command_chpkhw = [str(),
                               str('system-view'),
                               str('interface XGigabitEthernet0/0/16'),
                               str('undo port hybrid tagged vlan 1222'),
                               str('undo port hybrid tagged vlan 160'),
                               str('undo port hybrid tagged vlan 3250'),
                               #str('undo port hybrid tagged vlan 1227'),
                               #str('undo port hybrid tagged vlan 1228'),
                               str('undo port hybrid tagged vlan 423'),
#                               str('interface XGigabitEthernet0/0/21'),
#                               str('port hybrid tagged vlan 3250'),
                               str('interface XGigabitEthernet0/0/17'),
                               str('undo port hybrid tagged vlan 1222'),
                               #str('undo port hybrid tagged vlan 1227'),
                               #str('undo port hybrid tagged vlan 1228'),
                               str('quit'),
                               str('quit'),
                               str('save all'),
                               str('Y')
                              ]
        command_skl104 = [str('conf t'),
                               str('Interface GigabitEthernet3/9.1222'),
                               str('no shutdown'),
                               str('end'),
                               str('write')
                              ]
        pprint(command_beaver)
        pprint(command_chpkhw)
        pprint(command_skl104)
#        return 0
        r3 = chpk_hw.scripts.commands(commands=command_chpkhw)
        r1 = beaver.scripts.commands(commands=command_beaver)
        r2 = skl1047600.scripts.commands(commands=command_skl104)
        pprint(r1)
        pprint(r2)
        pprint(r3)

    def handle(self, *args, **options):
        path = None
        connect()
        path = options.get("path")
        pprint(path)
        if not path:
            self._usage()
        if path == '1':
           self.pathMain()
           return 0
        if path == '2':
           self.pathReserv()
           return 0
        if path == '3':
           self.pathSklady()
           return 0

if __name__ == "__main__":
    Command().run()

