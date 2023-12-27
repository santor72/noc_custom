import json
import re
from pprint import pprint
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from bson import ObjectId
from noc.sa.models.profile import Profile


connect()
p=Profile.objects.filter(name='MikroTik.RouterOS')[0]
routers =  ManagedObject.objects.filter(segment=ObjectId('65841a32a60f1bafc498b2fa'), profile=p)
routerscf={}
queryaddr="Match('virtual-router',A,'forwarding-instance',B, 'interfaces', Y, 'unit',C, 'inet','address',I)"
queryroute="Match('virtual-router',A,'forwarding-instance',B, 'route','inet','static',R,'next-hop',N)"
reip = re.compile(r'185\.83\.24.+')
reip1 = re.compile(r'185\.83\.240')
reip2 = re.compile(r'185\.83\.241')
for r in routers:
    routerscf[r.name] = {'id':r.id, 'name':r.name, 'ip':r.address, 'addr':[], 'route':[], 'ipcommnd':[], 'routecommand':[]}
    cf = r.get_confdb(cleanup=True)
    for a in cf.query(queryaddr):
        routerscf[r.name]['addr'].append(a)
    for a in cf.query(queryroute):
        routerscf[r.name]['route'].append(a)
for k,routercf in  routerscf.items():
    for i in routercf['addr']:
        if reip1.match(i['I'].address):
            #routercf.append(f"/ip address add address={i['I']}/{i['I'].mask} interface={i['Y']}")
            routercf['ipcommnd'].append(f"/ip address add address={reip1.sub('185.81.66' ,i['I'].address)}/{i['I'].mask} interface={i['Y']}")
            #print((f"/ip address add address={reip1.sub('185.81.66' ,i['I'].address)}/{i['I'].mask} interface={i['Y']}"))
        if reip2.match(i['I'].address):
            #routercf.append(f"/ip address add address={i['I']}/{i['I'].mask} interface={i['Y']}")
            routercf['ipcommnd'].append(f"/ip address add address={reip1.sub('185.81.67' ,i['I'].address)}/{i['I'].mask} interface={i['Y']}")
    for i in routercf['route']:
        if reip1.match(i['R'].address):
            #routercf.append(f"/ip route add dst-address={i['R']}/{i['R'].mask} gateway={i['N'].address}")
            routercf['routecommand'].append(f"/ip route add dst-address={reip2.sub('185.81.66' ,i['R'].address)} gateway={reip2.sub('185.81.66' ,i['N'].address)}")
        if reip2.match(i['R'].address):
            #routercf.append(f"/ip route add dst-address={i['R']}/{i['R'].mask} gateway={i['N'].address}")
            routercf['routecommand'].append(f"/ip route add dst-address={reip2.sub('185.81.67' ,i['R'].address)} gateway={reip2.sub('185.81.67' ,i['N'].address)}")
s = json.dumps({x['id']:{'name': x['name'], 'ip': x['ip'], 'ipcommnd':x['ipcommnd'], 'routecommand':x['routecommand']} for k,x in routerscf.items()})
for k,x in routerscf.items():
    for i in x['ipcommnd']:
        print(i)
