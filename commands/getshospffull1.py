# coding: utf-8
import textfsm
from bson import ObjectId
from tabulate import tabulate
import pickle
import pprint
from noc.core.mongo.connection import connect
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject

def parseoutput(tmpl, output):
   f = open(tmpl)
   re_table = textfsm.TextFSM(f)
   header = re_table.header
   result = re_table.ParseText(output)
   return {'header': header, 'result': result}



def process_output(l, result={}, router=None):
    t_path = '/opt/noc_custom/templates/ospf/topolograph'
    if not router.profile.name in result:
        result[router.profile.name] = {
            'router': [],
            'network': [],
            'external': [],
            'parsed': {
                'router': [],
                'network': [],
                'external': []
                }
         
        }
    result[router.profile.name]['router'].append(l[0])
    result[router.profile.name]['network'].append(l[1])
    result[router.profile.name]['external'].append(l[2])
    result[router.profile.name]['parsed' ]['router'].append(parseoutput('{}/{}_{}.tpl'.format(t_path, router.profile.name, 'router_p2p'), l[0]))
    result[router.profile.name]['parsed' ]['network'].append(parseoutput('{}/{}_{}.tpl'.format(t_path, router.profile.name, 'router_p2p'), l[1]))
    result[router.profile.name]['parsed' ]['external'].append(parseoutput('{}/{}_{}.tpl'.format(t_path, router.profile.name, 'router_p2p'), l[2]))

connect()
routers =  ManagedObject.objects.filter(segment=ObjectId('65841a32a60f1bafc498b2fa'))
action = Action.objects.get(name='getospffull')
res = {}
'''
output['Huawei.VRP'] = {
    'router' = []
    'network' = []
    'external' = []
}
'''
f=open(f"/tmp/ospfsh/sheremetyevo.txt",'w')
for router in routers:
 try:
    commands = str(action.expand(router,ospf_process=1)).split('\n')
    o = router.scripts.commands(commands=commands)
    if o['output']:
#        process_output(o['output'], res, router)
        f.write(pprint.pformat(o['output']))
        print(f"Router {router.name} is OK")
 except:
    print(f"Router {router.name} NOT OK")
f.close()
quit()
for profile in res:
    f = open('/tmp/'+profile+'.txt', 'w')
    f.write('\n'.join(res[profile]['router']))
    f.write('\n'.join(res[profile]['network']))
    f.write('\n'.join(res[profile]['external']))
    f.close()
with open('/tmp/ospfall.pickle', 'wb') as fp:
    pickle.dump(res,fp)
