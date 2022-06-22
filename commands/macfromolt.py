# coding: utf-8
from noc.core.mongo.connection import connect
from noc.core.management.base import BaseCommand
from noc.core.mac import MAC
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectselector import ManagedObjectSelector
import re

class Command(BaseCommand):
 def add_arguments(self, parser):
    parser.add_argument("-m", "--mac", dest="mac", default=None)

 def getmobyselector(self, selector_name=None):
        if selector_name:
           selector = ManagedObjectSelector.objects.filter(name=selector_name)
           s=[]
           mo=selector[0].managed_objects
           for item in mo:
            s.append(item.address)
           return s

 def get_macinfo(self,mac):
  rawmacs={}
  olt1 = self.getmobyselector('point-ZTEOLT-v1.2')
  olt2 = self.getmobyselector('point-ZTEOLT-v2')
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
  res= []
  for item in rawmacs:
    for s in rawmacs[item]:
      match = re_mac.match(s)
      if match:
         if re.search(r'^gpon', match.group('int')):
            mac_temp = MAC(match.group('mac'))
            if mac_temp == mac:
                res.append({'olt': item, 'int': match.group('int'), 'vlan': match.group('vlan')})
  return res

 def handle(self, *args, **options):
        connect()
        mac = options.get("mac")
        mac=MAC(mac)
        print(self.get_macinfo(mac))
        

if __name__ == "__main__":
    Command().run()
