# coding: utf-8
import textfsm
from bson import ObjectId
from tabulate import tabulate
import pickle
import pprint
from noc.core.mongo.connection import connect
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject


connect()
routers =  ManagedObject.objects.filter(segment=ObjectId('65841a32a60f1bafc498b2fa'), profile=ObjectId('5c496fe594c61c465e02e56f'))
action = Action.objects.get(name='getospffull')
res = {}
for router in routers:
 try:
    commands = str(action.expand(router,ospf_process=1)).split('\n')
    o = router.scripts.commands(commands=commands)
    if o['output']:
        res[router.id] = o['output']
        print(f"Router {router.name} is OK")
 except:
    print(f"Router {router.name} NOT OK")
with open('/tmp/ospf-sher.pickle', 'wb') as fp:
    pickle.dump(res,fp)
