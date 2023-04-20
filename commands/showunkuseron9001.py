import re
from noc.sa.interfaces.base import MACAddressParameter
from noc.bi.models.mac import MAC as MACDBC
from noc.core.mac import MAC
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
connect()
command = ['sh subscriber session  filter vrf point-unk  det | i Mac']
b = ManagedObject.objects.get(id=479)
r = b.scripts.commands(commands=command)
l = r['output'][0].split('\n')
macs = []
for i in l:
    if re.match(r'^Mac Address:',i):
        macs.append((i.split())[2])
macdb = MACDBC()
current = []
for i in macs:
    mac = int(MAC(MACAddressParameter(accept_bin=False).clean(i)))
    m=macdb.mac_filter({"mac": mac})
    if not m:
        current += [
            {
                "interface": '',
                "moname": '',
                "mo": '',
                "moip": '',
                'mac': i
                }
                ]
        continue
    y=0
    for p in m:
            if re.match(r'^gpon-olt',p["interface"]):
                mo = ManagedObject.objects.filter(bi_id=int(p["managed_object"]))
                mo = mo[0]
                command = [f"show mac {i}"]
                r=mo.scripts.commands(commands=command)
                x = [re.match(r'^.+(?P<int>gpon-onu_.+:\d+)\s+.+', x) for x in r['output'][0].split('\n') if re.findall('gpon-onu_', x)]
                if x:
                    ifname = x[0].group(1)
                else:
                    ifname = p["interface"]
                y=1
                current += [
                    {
                        "interface": ifname,
                        "moname": str(mo.name),
                        "mo": mo,
                        "moip": mo.address,
                        'mac': i
                    }
                    ]
                break
    if not y:
        current += [
            {
                "interface": '',
                "moname": '',
                "mo": '',
                "moip": '',
                'mac': i
                }
                ]
for i in current:
   xx = [i[x] for x in list(i.keys()) if x != 'mo']
   print(' - '.join(xx))
                    
