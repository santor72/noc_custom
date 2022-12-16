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

def get_mo(ips=[]):
    result = None
    for ip in ips:
        result = ManagedObject.objects.filter(address = ip, is_managed=True)
        if result:
            break
    return result

def addpeer(peer_rec, ospf_leaf):
    peer_mo = get_mo([peer[0], peer_address])
    if peer_mo:
        peer_record['bi_id'] = peer_mo.bi_id
    peers.append(peer_record)

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
                peer_record = {
                    'peer_id': m_ne.group('ip'),
                    'state': m_ne.group('state'),
                    'peer_address': '',
                    'interface': m_ne.group('interface'),
                    'area': m_ne.group('area'),
                    'bi_id': '',
                    'peer_int': ''
                  }
                )
                addpeer(peer_record, peers)
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
                    ospf[process_id] = {'routers':{}}
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
        ospfprocess = mo.scripts.commands(commands = ['show ip ospf   | i Routing Process'])
        prlst = ospfprocess['output'][0].split('\n')
        for pritem in prlst:
            m = re.match(r'^.+\"\S+\s+(?P<id>\d+)\"\s+with\s+ID\s+(?P<ip>\S+)$', pritem)
            if m:
                process_id = m.group('id')
                if p_id:
                    if p_id != process_id:
                        continue
                if not process_id in list(ospf.keys()):
                    ospf[process_id] = {'routers':{}}
                router_id = m.group('ip')
                ospf[process_id][mo.bi_id] = {'id': router_id, 'noc_id': mo.id, 'peers': []}
                ospf[process_id]['routers'][router_id] = mo.bi_id
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
        ospfne = mo.scripts.commands(commands = ['show ip ospf {} nei '.format(pid)])
        if not ospfne['output']:
            return -1
        l = ospfne['output'][0].split('\n')
        if l[0]:
            lst = l[1:]
        else:
            lst = l[2:]
        ne = {}
        re_area=re.compile(r".+In the area\s+(?P<area>\S+)\s+", re.MULTILINE | re.DOTALL)
        for neitem in lst:
            peer=neitem.split()
            if peer:
                peerdetail = mo.scripts.commands(commands = ['show ip ospf {} nei {} {}'.format(pid, peer[5], peer[0])])
                area=''
                if peerdetail['output']:
                    marea = re_area.match(peerdetail['output'][0])
                    if marea:
                        area = marea.group('area')
                peer_record = {
                    'peer_id': peer[0],
                    'state': peer[2],
                    'peer_address': peer[4],
                    'interface': peer[5],
                    'area': area,
                    'bi_id': '',
                    'peer_int': ''
                    }
                addpeer(peer_record, peers)
        return 1
    except:
        return -1

def get_ospf_peer_peers(mo, ospf, p_id, notfound):
    #try:
        if not mo.profile.name.replace('.','_')+'_get_ospf_peers_all' in globals():
            if not mo.address in notfound:
                notfound.append({mo.address:'no getter'})
            return -1
        r = globals()[mo.profile.name.replace('.','_')+'_get_ospf_peers_all'](mo,ospf,p_id)
        if r != 1:
            if not mo.address in notfound:
                notfound.append({mo.address:'peers get error'})
            return -1
        print(len(ospf[p_id][mo.bi_id]['peers']))
        for p in ospf[p_id][mo.bi_id]['peers']:
            r = ManagedObject.objects.filter(address = p['peer_id'], is_managed=True)
            if r:
                if not p['peer_id'] in list(oospf[p_id]['routers'].keys()):
                        ospf[p_id]['routers'] = { p['peer_id']: r.bi_id}
                if not r[0].bi_id in ospf[p_id]:
                    print('Leaf peer {}'.format(r[0].name))
                    get_ospf_peer_peers(r[0], ospf, p_id,notfound)
            else:
                if not p['peer_id'] in list(oospf[p_id]['routers'].keys()):
                        ospf[p_id]['routers'] = { p['peer_id']: ''}
                if not p['peer_id'] in notfound:
                    notfound.append({p['peer_id']:'MO noit found'})
                continue
        return 1
    #except:
    #    notfound.append(mo.address)
    

def handler():
    ospf_topo={}        
    area0routers =  ManagedObject.objects.filter(labels__contains=[' ospf_16143_area0'])
    for router in area0routers:
        routerprofile = router.profile.name.replace('.','_')
        globals()[routerprofile+'_get_ospf_peers_all'](router,ospf_topo,'16143')
        break
    notfound = []
    ospf1 = copy.deepcopy(ospf_topo)
    for proc_item in ospf1.keys():
        for router_item in ospf1[proc_item].keys():
            for peer_item in ospf1[proc_item][router_item]['peers']:
                router = ManagedObject.objects.filter(address = peer_item['peer_id'], is_managed=True)
                if router:
                    if not peer_item['peer_id'] in list(ospf_topo[proc_item]['routers'].keys()):
                        ospf_topo[proc_item]['routers'] = { peer_item['peer_id']: router.bi_id}
                    if not router[0].bi_id in list(ospf_topo[proc_item].keys()):
                        print('Core peer {}'.format(router[0].name))
                        get_ospf_peer_peers(router[0], ospf_topo, proc_item,notfound)
                else:
                    if not peer_item['peer_id'] in list(ospf_topo[proc_item]['routers'].keys()):
                        ospf_topo[proc_item]['routers'] = { peer_item['peer_id']: router.bi_id}
                    if not peer_item['peer_id'] in notfound:
                        notfound.append({peer_item['peer_id']:'MO not found'})
                    continue
    with open('/tmp/ospf_topo.pickle', 'wb') as f:
        pickle.dump(ospf_topo, f)
    with open('/tmp/ospf_notfound.pickle', 'wb') as f:
        pickle.dump(notfound, f)
    pprint(ospf_topo)

