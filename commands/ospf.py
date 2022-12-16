# coding: utf-8
#python modules
import re
from pprint import pprint
import pickle
import copy

#NOC modules
from noc.core.mongo.connection import connect
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.subinterface import SubInterface
def make_link(router_bi_id, router_id, peer,links):
    '''
    Формируем запись о связи маршрутизаторов
    {
        type: noc
        mo1 : {bi_id: interface}
        mo2 : {bi_id: interface}
        ИЛИ
        type: router
        ip1 : ip
        ip2: ip
    }
    Проверяем данные о mo и interface в peer_item
    если хоть одного нет type router
    Проверяем наличие в словаре links такой связи
    если нет добавляем
    '''
    link={'type':'unk'}
    y = 0
    if peer['bi_id'] and peer['interface_id'] and peer['peer_int_id']:
        for item in links:
            if 'mo1' in item.keys()  and 'mo2' in item.keys():
                if (item['mo1'] == {router_bi_id:peer['interface_id']}) and (item['mo2'] == {peer['bi_id']:peer['interface_id']}):
                    y = 1
                if (item['mo2'] == {router_bi_id:peer['interface_id']}) and (item['mo1'] == {peer['bi_id']:peer['interface_id']}):
                    y = 1
            if y == 1:
                break
            link['type']='noc'
            link['mo1'] = {router_bi_id:peer['interface_id']}
            link['mo2'] = {peer['bi_id']:peer['interface_id']}
            link['ip1'] = router_id
            link['ip2'] = peer['peer_id']
    else:
        for item in links:
            if 'ip1' in item.keys()  and 'ip2' in item.keys():
                if (item['ip1'] == router_id) and (item['ip2'] == peer['peer_id']):
                    y = 1
                if (item['ip2'] == router_id) and (item['ip1'] == peer['peer_id']):
                    y = 1
            if y == 1:
                break
            link['type']='router'
            link['ip1'] = router_id
            link['ip2'] = peer['peer_id']
    return link

def get_mo(ips=[]):
    for ip in ips:
        result = ManagedObject.objects.filter(address = ip, is_managed=True)
        if result:
            return result[0]
    for ip in ips:
        si = SubInterface.objects.filter(ipv4_addresses__contains=ip)
        if si:
            for s in si:
                if re.findall(rf";{ip}/\d\d;", f";{';'.join(s.ipv4_addresses)};"):
                    if s.managed_object.is_managed:
                        return s.managed_object
    return None

def get_ifname_by_ip(ip):
    si = SubInterface.objects.filter(ipv4_addresses__contains=ip)
    if si:
        for s in si:
            if re.findall(rf";{ip}/\d\d;", f";{';'.join(s.ipv4_addresses)};"):
                if s.managed_object.is_managed:
                    return s.name
    return ''

def get_ifid_by_ip(ip):
    si = SubInterface.objects.filter(ipv4_addresses__contains=ip)
    if si:
        for s in si:
            if re.findall(rf";{ip}/\d\d;", f";{';'.join(s.ipv4_addresses)};"):
                if s.managed_object.is_managed:
                    return s.id
    return ''

def get_interface_by_ip(ip):
    si = SubInterface.objects.filter(ipv4_addresses__contains=ip)
    if si:
        for s in si:
            if re.findall(rf";{ip}/\d\d;", f";{';'.join(s.ipv4_addresses)};"):
                if s.managed_object.is_managed:
                    return s
    return None

def get_mo_bi(ips=[]):
    mo = get_mo(ips)
    if mo:
        return mo.bi_id
    else:
        return None

def Huawei_VRP_get_ospf_process_peers(mo=None, pid=None, peers=[]):
    try:
        if not mo:
            return 0
        if not pid:
            return 0
        ospfne = mo.scripts.commands(commands = ['dis ospf {} peer  brief'.format(pid)])
        if not ospfne['output']:
            return -1
        l = ospfne['output'][0].split('\n')
        re_peer = re.compile(r"^.+(?P<area>\d+.\d+.\d+.\d+)\s+(?P<interface>\S+)\s+(?P<ip>\d+.\d+.\d+.\d+)\s+(?P<state>\S+)\s+")
        for neitem in l:
            m_ne = re_peer.match(neitem)
            if m_ne:
                peers.append({
                    'peer_id': m_ne.group('ip'),
                    'state': m_ne.group('state'),
                    'peer_address': '',
                    'interface': m_ne.group('interface'),
                    'interface_id': '',
                    'area': m_ne.group('area'),
                    #Ищем ManagedObject по адресам пира
                    'bi_id': get_mo_bi([m_ne.group('ip')]),
                    #Ищем интерфейс пира по адресам пира
                    #Имя интерфейса из noc не совпадает с полным имененм на оборудовании
                    'peer_int': '',
                    'peer_int_id': ''
                })
        return 1
    except:
        return -1

def Huawei_VRP_get_ospf_peers_all(mo=None,ospf={}, p_id=None):
    try:
        if not mo:
            return 0
        ospfprocess = mo.scripts.commands(commands = ['dis ospf asbr-summary | i OSPF'])
        prlst = ospfprocess['output'][0].split('\n')
        for pritem in prlst:
            m = re.match(r'^\s+OSPF Process\s+(?P<id>\d+)\s+with\s+Router\s+ID\s+(?P<ip>\S+)$', pritem)
            if m:
                process_id = m.group('id')
                if p_id:
                    if p_id != process_id:
                        continue
                if not process_id in list(ospf.keys()):
                    ospf[process_id] = {'routers':{}, 'links': []}
                router_id = m.group('ip')
                ospf[process_id][mo.bi_id] = {'id': router_id, 'noc_id': mo.id, 'peers': []}
                ospf[process_id]['routers'][router_id] = mo.bi_id
                Huawei_VRP_get_ospf_process_peers(mo, process_id, ospf[process_id][mo.bi_id]['peers'])
        return 1
    except:
        return -1

def Cisco_IOS_get_ospf_peers_all(mo=None,ospf={}, p_id=None):
    try:
        if not mo:
            return -1
        #Ищем все процессы
        ospfprocess = mo.scripts.commands(commands = ['show ip ospf   | i Routing Process'])
        prlst = ospfprocess['output'][0].split('\n')
        #обрабатываем процессы
        for pritem in prlst:
            m = re.match(r'^.+\"\S+\s+(?P<id>\d+)\"\s+with\s+ID\s+(?P<ip>\S+)$', pritem)
            if m:
                process_id = m.group('id')
                #Если нужен опреденный процесс идем дальше
                if p_id:
                    if p_id != process_id:
                        continue
                #создаем процесс в словаре
                if not process_id in list(ospf.keys()):
                    ospf[process_id] = {'routers':{}, 'links': []}
                #Назначем id маршрутизатора
                router_id = m.group('ip')
                ospf[process_id][mo.bi_id] = {'id': router_id, 'noc_id': mo.id, 'peers': []}
                ospf[process_id]['routers'][router_id] = mo.bi_id
                #Запускаем поиск пиров
                Cisco_IOS_get_ospf_process_peers(mo, process_id, ospf[process_id][mo.bi_id]['peers']) 
        return 1
    except:
        return -1       

def Cisco_IOS_get_ospf_process_peers(mo=None, pid=None, peers=[]):
    try:
        if not mo:
            return 0
        if not pid:
            return 0
        #Получаем список пиров
        ospfne = mo.scripts.commands(commands = ['show ip ospf {} nei '.format(pid)])
        if not ospfne['output']:
            return -1
        l = ospfne['output'][0].split('\n')
        if l[0]:
            lst = l[1:]
        else:
            lst = l[2:]
        ne = {}
        #regexp для поиска ospf area
        re_area=re.compile(r".+In the area\s+(?P<area>\S+)\s+", re.MULTILINE | re.DOTALL)
        #Идем по строкам ввывода комманды
        for neitem in lst:
            peer=neitem.split()
            if peer:
                #Detail пира
                peerdetail = mo.scripts.commands(commands = ['show ip ospf {} nei {} {}'.format(pid, peer[5], peer[0])])
                area=''
                #Ищем ospf area
                if peerdetail['output']:
                    marea = re_area.match(peerdetail['output'][0])
                    if marea:
                        area = marea.group('area')
                #Ищем ip адрес интерфейса на маршрутизаторе
                #Имя интерфейса из noc не совпадает с полным именем на оборудовании
                #А нам надо найти объект интерфейс в ноке
                a = mo.scripts.commands(commands = ['show interfaces {} | i Internet address'.format(peer[5])])
                if a and a['output']:
                    a1 = re.findall(r'^\s+Internet\s+address\s+is\s+(?P<ip>\d+.\d+.\d+.\d+)/\d+\d+', a['output'][0])
                    interface_id = get_ifid_by_ip(a1[0]) if a1 else ''
                else:
                    interface_id = ''
                peers.append({
                    'peer_id': peer[0],
                    'state': peer[2],
                    'peer_address': peer[4],
                    'interface': peer[5],
                    'interface_id': interface_id,
                    'area': area,
                    #Ищем ManagedObject по адресам пира
                    'bi_id': get_mo_bi([peer[0],peer[4]]),
                    #Ищем интерфейс пира по адресам пира
                    #Имя интерфейса из noc не совпадает с полным имененм на оборудовании
                    'peer_int': get_ifname_by_ip(peer[4]),
                    'peer_int_id': get_ifid_by_ip(peer[4])
                })
        return 1
    except:
        return -1

def get_ospf_peer_peers(mo, ospf, p_id, notfound):
    try:
        #Ищем ManagedObject
        if not mo.profile.name.replace('.','_')+'_get_ospf_peers_all' in globals():
            if not mo.address in notfound:
                notfound.append({mo.address:'no getter'})
            return -1
        #Если нашли опрашиваем
        r = globals()[mo.profile.name.replace('.','_')+'_get_ospf_peers_all'](mo,ospf,p_id)
        if r != 1:
            if not mo.address in notfound:
                notfound.append({mo.address:'peers get error'})
            return -1
        print(len(ospf[p_id][mo.bi_id]['peers']))
        #Опрашиваем его пиры
        for p in ospf[p_id][mo.bi_id]['peers']:
            r = ManagedObject.objects.filter(address = p['peer_id'], is_managed=True)
            if r:
                if not p['peer_id'] in list(ospf[p_id]['routers'].keys()):
                        ospf[p_id]['routers'][p['peer_id']] = r.bi_id
                if not r[0].bi_id in ospf[p_id]:
                    print('Leaf peer {}'.format(r[0].name))
                    get_ospf_peer_peers(r[0], ospf, p_id,notfound)
            else:
                if not p['peer_id'] in list(ospf[p_id]['routers'].keys()):
                        ospf[p_id]['routers'][p['peer_id']] = ''
                if not p['peer_id'] in notfound:
                    notfound.append({p['peer_id']:'MO noit found'})
                continue
        return 1
    except:
        notfound.append(mo.address)
    

def handler():
    ospf_topo={}        
    #Опрашиваем маршрутизаторы в area 0
    area0routers =  ManagedObject.objects.filter(labels__contains=[' ospf_16143_area0'])
    for router in area0routers:
        routerprofile = router.profile.name.replace('.','_')
        print('core router process '+ router.address)
        globals()[routerprofile+'_get_ospf_peers_all'](router,ospf_topo,'16143')
    notfound = []
    ospf1 = copy.deepcopy(ospf_topo)
    #Опрашиваем маршрутизаторы найденные на коневых роутерах
    for proc_item in ospf1:
        print(proc_item)
        for router_item in ospf1[proc_item]:
            if router_item == 'routers' or router_item == 'links':
                continue
            for peer_item in ospf1[proc_item][router_item]['peers']:
                router = ManagedObject.objects.filter(address = peer_item['peer_id'], is_managed=True)
                if router:
                    if not peer_item['peer_id'] in list(ospf_topo[proc_item]['routers'].keys()):
                        ospf_topo[proc_item]['routers'][peer_item['peer_id']] = router[0].bi_id
                    if not router[0].bi_id in list(ospf_topo[proc_item].keys()):
                        print('Core peer {}'.format(router[0].name))
                        get_ospf_peer_peers(router[0], ospf_topo, proc_item,notfound)
                else:
                    if not peer_item['peer_id'] in list(ospf_topo[proc_item]['routers'].keys()):
                        ospf_topo[proc_item]['routers'][peer_item['peer_id']] = ''
                    if not peer_item['peer_id'] in notfound:
                        notfound.append({peer_item['peer_id']:'MO not found'})
                    continue
    #Формируем словарь связей
    for proc_item in ospf_topo:
        for router_item in ospf_topo[proc_item]:
            if router_item == 'routers' or router_item == 'links':
                continue
            for peer_item in ospf_topo[proc_item][router_item]['peers']:
                newlink=make_link(router_item, ospf_topo[proc_item][router_item]['id'], peer_item,ospf_topo[proc_item]['links'])
                ospf_topo[proc_item]['links'].append(newlink)
    with open('/tmp/ospf_topo.pickle', 'wb') as f:
        pickle.dump(ospf_topo, f)
    with open('/tmp/ospf_notfound.pickle', 'wb') as f:
        pickle.dump(notfound, f)
    pprint(ospf_topo)

if __name__ == "__main__":
    connect()
    handler()
