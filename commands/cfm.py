import requests

#NOC modules
from noc.main.models.customfieldenumgroup import CustomFieldEnumGroup
from noc.main.models.customfieldenumvalue import CustomFieldEnumValue
from noc.fm.models.activeevent import ActiveEvent
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect
from noc.sa.models.action import Action

#номер справочника с rmep в enum groups
cfmrmep_EG = 10
keys = "moid;moname;md;ma;rmep;interface;shutdowndown;alarm"
tel_url='https://api.telegram.org/bot686384604:AAEbjmxrTHJP9ZlgQg53odgCML-egZZtI1g/sendMessage?chat_id=-1001264455094&text='

#поднимет интерфейс, реализован на actions
def int_goup(m,i):
    action = Action.objects.get(name='interface_up')
    cmd = str(action.expand(m,ifname=i))
    return m.scripts.commands(commands=cmd.split("\n"))

def int_godown(m,i):
    action = Action.objects.get(name='interface_shutdown')
    cmd = str(action.expand(m,ifname=i))
    return m.scripts.commands(commands=cmd.split("\n"))

#Обработчик отключения rmep
#ищет запись в EnumGroups для cfm по MO.id md ma rmep из эвента
#постит в теграм если alarm == 1 и кладет интерфейс если dodown == 1
def rmep_down(event):
    global cfmrmep_EG
    global tel_url
    connect()
    mo = event.managed_object
    rstr = f""
    md = event.vars.get('md')
    ma = event.vars.get('ma')
    rmep = event.vars.get('rmep')
    values = CustomFieldEnumValue.objects.filter(enum_group=eg, value__regex = r"{};.+$".format(mo.id))
    values_list = [x.value.split(';') for x in values]
    eg = CustomFieldEnumGroup.objects.get(cfmrmep_EG)
    for y in values_list:
        md1 = y[2]
        ma1 = y[3]
        rmep1 = y[4]
        if md == md1 and ma == ma1 rmep == rmep1:
            if y[7] == 1:
                msg = f"CFM alarm rmep for protect interface {y[5]} disconnected."
                response =  requests.post(tel_url + msg, headers=headers)
            if y[6]:
                resdown = int_godown(mo,y[5])

#Обработчик включения rmep
#ищет запись в EnumGroups для cfm по MO.id md ma rmep из эвента
#постит в теграм если alarm == 1 и поднимет интерфейс если dodown == 1
def rmep_up(event):
    global cfmrmep_EG
    global tel_url
    connect()
    mo = event.managed_object
    rstr = f""
    md = event.vars.get('md')
    ma = event.vars.get('ma')
    rmep = event.vars.get('rmep')
    values = CustomFieldEnumValue.objects.filter(enum_group=eg, value__regex = r"{};.+$".format(mo.id))
    values_list = [x.value.split(';') for x in values]
    eg = CustomFieldEnumGroup.objects.get(cfmrmep_EG)
    for y in values_list:
        md1 = y[2]
        ma1 = y[3]
        rmep1 = y[4]
        if md == md1 and ma == ma1 rmep == rmep1:
            if y[7] == 1:
                msg = f"CFM alarm rmep for protect interface {y[5]} is UP."
                response =  requests.post(tel_url + msg, headers=headers)
            if y[6]:
                resup = int_goup(mo,y[5])

mo1=ManagedObject.objects.get(id=681)
