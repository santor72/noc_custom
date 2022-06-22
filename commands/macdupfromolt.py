# coding: utf-8
from noc.core.mongo.connection import connect
from noc.core.management.base import BaseCommand
from noc.core.mac import MAC
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
import re

class Command(BaseCommand):

 def getmobyselector(self, selector_name=None):
        if selector_name:
           selector = ManagedObjectSelector.objects.filter(name=selector_name)
           s=[]
           mo=selector[0].managed_objects
           for item in mo:
            s.append(item.address)
           return s

 def get_dm(self):
  rawmacs={}
  olt1 = self.getmobyselector(self, 'point-ZTEOLT-v1.2')
  olt2 = self.getmobyselector(self, 'point-ZTEOLT-v2')
  re_mac = re.compile(r'^(?P<mac>\S\S\S\S.\S\S\S\S.\S\S\S\S)\s+(?P<vlan>\d+)\s+\S+\s+(?P<int>\S+)')
  for item in olt1:
    try:
        olt = ManagedObject.objects.filter(address=item)
        cmd = ['show mac']
        if not olt:
            continue
        output = olt[0].scripts.commands(commands=cmd)
        rawmacs[item] = output['output'][0].split('\n')
    except:
        continue
  for item in olt2:
    try:
        olt = ManagedObject.objects.filter(address=item)
        cmd = ['show mac']
        if not olt:
            continue
        output = olt[0].scripts.commands(commands=cmd)
        rawmacs[item] = output['output'][0].split('\n')
    except:
        continue
  macs= {}
  for item in rawmacs:
    for s in rawmacs[item]:
      match = re_mac.match(s)
      if match:
         if re.search(r'^gpon', match.group('int')):
            if not match.group('mac') in macs.keys():
                macs[match.group('mac')]=[]
            macs[match.group('mac')].append({'olt': item, 'int': match.group('int'), 'vlan': match.group('vlan')})
  for item in macs:
   if len(macs[item]) > 1:
    print(item)
    for i in range(len(macs[item])):
        print(f"{macs[item][i]['olt']} - {macs[item][i]['int']} - {macs[item][i]['vlan']}")


    def handle(self, *args, **options):
        connect()
        self.get_dm(self)

if __name__ == "__main__":
    Command().run()
