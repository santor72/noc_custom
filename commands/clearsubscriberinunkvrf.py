import re
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
import pprint
connect()
command = ['show subscriber session  filter vrf point-unk']
b = ManagedObject.objects.get(id=479)
r = b.scripts.commands(commands=command)
int=[]
l = r['output'][0].split('\n')
for i in l:
  if re.match(r'^PPPoE:PTA',i):
   int.append((i.split())[1])
cmd=[]
for i in int:
    cmd.append(f"clear subscriber session identifier interface {i}")
#print.pprint(cmd)    
import time
time.sleep(5)
r2 = b.scripts.commands(commands=cmd)
cmd2 = ['show subscriber session  filter vrf point-unk summary location 0/RSP0/CPU0']
time.sleep(5)
r3 = b.scripts.commands(commands=cmd2)
pprint.pprint(r3['output'][0].split('\n'))

