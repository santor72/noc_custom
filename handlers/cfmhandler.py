"""
Задача переключить VPWS на backup PE при отключении связи Primary PE <-> CE
решаемая проблема - если CE подключен через несколько коммутаторов от Primary PE
то автоматического переключения не происходит

Общий обработчик для изменения состояния CFM
При отключении сессии cfm MO присылает сообщение remote mep disconnected/connected
Обработчик по mo из event выбирает все сервисы (sa->Services)
формирует словарь из Capability сервиса
ищет совпадение по md, ma, rmep
Выбирает список Capability типа Network | CFM | Interface
и вызывает для них процедуру отключения/включения на данном MO
Проект - если есть Capability Network | CFM | Handler
то загружается модуль из custom.cfmhandlers и запускается процедура run

Capability для сервиса
Network | CFM | MD
Network | CFM | MA
Network | CFM | Rmep
Network | CFM | Interface
Network | CFM | Handler
"""
import requests
import pickle
from pprint import pformat

#NOC modules
from noc.main.models.customfieldenumgroup import CustomFieldEnumGroup
from noc.main.models.customfieldenumvalue import CustomFieldEnumValue
from noc.fm.models.activeevent import ActiveEvent
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect
from noc.sa.models.action import Action
from noc.sa.models.service import Service
from noc.inv.models.capability import Capability
from noc.wf.models.workflow import Workflow
from noc.wf.models.state import State

#номер справочника с rmep в enum groups
cfmrmep_EG = 10
keys = "moid;moname;md;ma;rmep;interface;shutdowndown;alarm"
tel_url='https://api.telegram.org/bot686384604:AAEbjmxrTHJP9ZlgQg53odgCML-egZZtI1g/sendMessage?chat_id=-1001264455094&text='
headers = {'Content-type': 'application/json'}
sendalarm = 1

#поднимет интерфейс, реализован на actions
def int_goup(m,i):
    action = Action.objects.get(name='interface_up')
    cmd = str(action.expand(m,ifname=i))
    return m.scripts.commands(commands=cmd.split("\n"))

def int_godown(m,i):
    action = Action.objects.get(name='interface_shutdown')
    cmd = str(action.expand(m,ifname=i))
    return m.scripts.commands(commands=cmd.split("\n"))
#Словарь с данными capabilities сервиса
def parsecaps(p_service:Service):
    result = {
        'md':'',
        'ma':'',
        'rmep':0,
        'interfaces':[],
        'handler':''
    }
    for c in p_service.caps:
        if c.capability.name == 'Network | CFM | MD':
            result['md'] = c.value
        elif c.capability.name == 'Network | CFM | MA':
            result['ma'] = c.value
        elif c.capability.name == 'Network | CFM | Rmep':
            result['rmep'] = c.value
        elif c.capability.name == 'Network | CFM | Handler':
            result['handler'] = c.value            
        elif c.capability.name == 'Network | CFM | Interface':
            result['interfaces'].append(c.value)
        else:
            pass
    return result

#Обработчик отключения rmep
def rmep_down(event):
    global cfmrmep_EG
    global tel_url
    global headers
    global sendalarm
    if not event:
       return None
    connect()
    mo = event.managed_object
    services = Service.objects.filter(managed_object = mo)
    services_parced = [{'service':x,'caps': parsecaps(x)} for x in services]
    istarget = lambda c,e: True if c['md'] == e.vars.get('md') and c['ma'] == e.vars.get('ma') and c['rmep'] == e.vars.get('rmep') else Flase
    services_target = [x for x in services_parced if istarget(x['caps'], event)]
    description = ''
    for y in services_target:
        try:
            stateDown = State.objects.get(name='Down', workflow = y['service'].profile.workflow)
            y['service'].state=stateDown
            y['service'].save()
        except:
            pass
        if not description:
           description = y['service'].description
        if y['caps']['interfaces']:
           for i in y['caps']['interfaces']:
             print(f"Interface {i} go down")
             resdown = int_godown(mo,i)
    if sendalarm == 1:
                msg = [f"Alarm on {mo.name}"]
                msg.append(f"IP: {mo.address}")
                msg.append(f"Remote device disconnected.")
                if description:
                   msg.append(f"For service {description}.")
#                print('\n'.join(msg))
                response =  requests.post(tel_url + '\n'.join(msg), headers=headers)

#Обработчик включения rmep
def rmep_up(event):
#    with open("/tmp/e.pickle", "wb") as f:
#       pickle.dump(event, f)
    global cfmrmep_EG
    global tel_url
    global headers
    global sendalarm
    connect()
    mo = event.managed_object
    services = Service.objects.filter(managed_object = mo)
    services_parced = [{'service':x,'caps': parsecaps(x)} for x in services]
    istarget = lambda c,e: True if c['md'] == e.vars.get('md') and c['ma'] == e.vars.get('ma') and c['rmep'] == e.vars.get('rmep') else Flase
    services_target = [x for x in services_parced if istarget(x['caps'], event)]
    description = ''
    for y in services_target:
        try:
            stateOk = State.objects.get(name='Ok', workflow = y['service'].profile.workflow)
            y['service'].state=stateOk
            y['service'].save()
        except:
            pass
        if not description:
           description = y['service'].description
        if y['caps']['interfaces']:
           for i in y['caps']['interfaces']:
             print(f"Interface {i} go up")
             resup = int_goup(mo,i)
    if sendalarm == 1:
                msg = [f"Alarm cleared on {mo.name}"]
                msg.append(f"IP: {mo.address}")
                msg.append(f"Remote device connected.")
                if description:
                   msg.append(f"For service {description}.")
#                print('\n'.join(msg))
                response =  requests.post(tel_url + '\n'.join(msg), headers=headers)

