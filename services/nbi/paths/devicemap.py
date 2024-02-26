# Python modules
from __future__ import absolute_import
import time
import os
import sys
import json
import requests
import re
import netaddr
import networkx as nx
from pprint import pformat
from typing import List, Union, Dict, Optional

# Third-party modules
from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# NOC modules
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.inv.models.link import Link
from noc.core.mongo.connection import connect

router = APIRouter()
usdevtypes={2:'system_device', 3:'switch', 4:'radio'}
ussysdevtype =2

class TopologyInfo:
    nodes=None
    links=None
    current_link_id = 1
    current_node_id = 1
    node_id_map = None
    link_id_map = None
    hideip=['217.76.46.127', '217.76.46.118']
#Возвращает id из словаря links по хешу линка
    def map_link_id(self, link_hash):
        for l in self.links:
            if link_hash == self.links[l].get('hash'):
                return self.links[l].get('id')
        return 0
#возвращает id из словаря nodes по хешу устройства
    def map_node_id(self, node_hash):
        for n in self.nodes:
            if node_hash == self.nodes[n].get('hash'):
                return n.get('id')
        return 0
#Новое устройство из данных userside    
    def newUSnode(self,devdata):
        newid=self.current_node_id
        self.current_node_id+=1
        if devdata['devtyper']==3:
            dtype="switch"
            type = 'device'
        elif devdata['devtyper']==4:
            dtype = "radio"
            type = 'device'
        elif devdata['devtyper']==2:
            dtype = "system_device"            
            type = 'cloud'
        else:
            dtype = "unk"
            type = 'device'
        if not devdata.get('host'):
            devdata['host'] = '255.255.255.'+str(newid)
        self.nodes[newid] = {
            'id': newid,
            'devtyper': devdata['devtyper'],
            'dtype': dtype,
            'hash': self.generate_node_hash(devdata['host']),
            'system': 'userside',
            'type': type,
            'device_id': devdata['ID'],
            'host': devdata['host'],
            'ip': devdata['host'],
            'location': devdata['location'] if devdata['location'] else '',
            'name': devdata['name'] or devdata['nazv'],
            'devsegment':'Access',
            'interfaces': devdata['ifaces'],
            'uplink_interfaces': devdata['uplink_iface_array'],
            'downlink_interfaces': devdata.get('dnlink_iface_array'),
            'linktext': devdata.get('linktext')
        }
        self.node_id_map.append({'id':newid, 'hash': self.generate_node_hash(devdata['host'])})
        return newid

    def newUSlink(self,a,b, inta, intb,cid):
        if a['type'] != 'customer':
            newlinkhash = self.generate_link_hash(a['ip'], b['ip'], inta['ifIndex'], intb['ifIndex'])
            if self.map_link_id(newlinkhash):
                return 0
        else:
            newlinkhash = f"c-1-{b['host']}-{intb['ifIndex']}"
        newlinkid=self.current_link_id
        self.current_link_id+=1
        linktext=''
        if a.get('linktext'):
            linktext += a.get('linktext')
        elif b.get('linktext'):
            linktext += ' ' + b.get('linktext')
        self.links[newlinkid]={
            'id' : newlinkid,
            'connect_id': cid,
            'hash': newlinkhash,
            'system': 'userside',
            'nodea': a['id'],
            'nodeb':b['id'],
            'linktext': linktext,
            'inta':{'ifindex': inta['ifIndex'], 'ifname': inta['ifName']},
            'intb': {'ifindex': intb['ifIndex'], 'ifname': intb['ifName']}
            }
        self.node_id_map.append({'id':newlinkid, 'hash': newlinkhash})
        return newlinkid

#Новое устройство из данных NOC
    def newNOCnode(self,mo):
        newid = self.findnode_id_byip(mo.address)
        if newid:
            return newid
        newid=self.current_node_id
        self.current_node_id+=1
        if mo.object_profile.shape == 'Cisco/layer_3_switch':
            icon = 'switchwithborder'
        elif mo.object_profile.shape == 'Cisco/router':
            icon = 'router'
        elif mo.object_profile.shape == 'Cisco | File Server':
            icon = 'server'
        else:
            icon = 'switch'
        self.nodes[newid] = {
            'id': newid,
            'type': 'device',
            'devsegment':'Access',
            'hash': self.generate_node_hash(mo.address),
            'system': 'noc',
            'device_id': mo.id,
            'host': mo.address,
            'ip': mo.address,
            'location': mo.description,
            'name': mo.name,
            'interfaces': {},
            'uplink_interfaces': {},
            'icon': icon
        }
        self.node_id_map.append({'id':newid, 'hash': self.generate_node_hash(mo.address)})
        return newid

    def newNOClink(self,a,b, inta, intb):
        newlinkhash = self.generate_link_hash(self.nodes[a]['ip'], self.nodes[b]['ip'], inta['ifIndex'], intb['ifIndex'])
        if self.map_link_id(newlinkhash) or newlinkhash == 0:
            return 0
        newlinkid=self.current_link_id
        self.current_link_id+=1
        self.links[newlinkid]={
            'id' : newlinkid,
            'hash': newlinkhash,
            'system': 'noc',
            'nodea': a,
            'nodeb':b,
            'inta':{'ifindex': inta['ifIndex'], 'ifname': inta['ifName']},
            'intb': {'ifindex': intb['ifIndex'], 'ifname': intb['ifName']}
            }
        self.link_id_map.append({'id':newlinkid, 'hash': newlinkhash})
        return newlinkid

    #ищет запись о устройстве с nodes по id в учетной системе
    def findnode_by_device_id(self,object_id,extsys):
        for x in self.nodes.keys():            
            if object_id == self.nodes[x].get('device_id') and extsys == self.nodes[x].get('system'):
                return x
        return 0

    def findnode_id_byip(self, ip):
        for x in self.nodes.keys():            
            if ip == self.nodes[x].get('ip'):
                return x
        return 0
    
    def generate_node_hash(self,ipstr=None):
        ip = netaddr.IPAddress(ipstr)
        return ip.value

    def generate_link_hash(self,ip1,ip2,ifnum1,ifnum2):
        if ip1 > ip2:
            idstr=f"{ip2}-{ifnum2}-{ip1}-{ifnum1}"
        elif ip1 < ip2:
            idstr=f"{ip1}-{ifnum1}-{ip2}-{ifnum2}"
        else:
            return 0
        return idstr

    def generatejs(self, to_core):
        if to_core == 1:
            return self.generate_full()
        else:
            return self.generate_to_asbr()

    def generate_to_asbr(self):
        topology_dict = {'nodes': [], 'links': []}
        asbrid = 0 
        fistnode = self.nodes[(list(self.nodes.keys()))[0]]['id']
        for k,item in self.nodes.items():
            if item['host'] == '217.76.46.100' or item['ip'] == '217.76.46.100':
                asbrid = item['id']
        if asbrid != 0:
            edge_labels={}
            G = nx.Graph()
            for k,v in self.nodes.items():
                G.add_node(v['id'])
            for k,item in self.links.items():
                G.add_edge(item['nodea'], item['nodeb'])
            pos =  nx.spring_layout(G)
            path = nx.shortest_path(G,source=fistnode,target=asbrid)
            path_edges = list(zip(path,path[1:]))
            if path_edges:
                for k,item in self.nodes.items():
                    if not (k in path):
                        continue
                    if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82']:
                        name= f"ММТС-9 {item.get('host')}"
                    elif item.get('ip') in ['217.76.46.100','217.76.46.127']:
                        name = f"ASBR {item.get('host')}"
                    elif item['type'] == 'cloud':
                        name = item.get('name') if item.get('name') else item.get('location')
                    else:
                        name = item.get('host')                    
                    if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82']:
                        icon = 'cloud'
                    elif item.get('ip') in ['217.76.46.100','217.76.46.127']:
                        icon = 'cloud'
                    elif item.get('icon'):
                        icon = item.get('icon')
                    elif item['type'] == 'customer':
                        icon = 'host'
                    elif item['type'] == 'cloud':
                        icon = 'cloud'                        
                    else:
                        icon = 'switch'
                    topology_dict['nodes'].append({
                        'id': int(item['id']),
                        'name': name,
                        'primaryIP': item.get('host') or item.get('ip'),
                        'nazvanie': item.get('nazv'),
                        'location': item.get('location'),
                        'icon':  icon,
                        'segment': item.get('devsegment')
                    })
                for k,item in self.links.items():
                    if not (item['nodea'] in path and item['nodeb'] in path):
                        continue
                    topology_dict['links'].append({
                        'id': int(item['id']),
                        'source': int(item['nodea']),
                        'target': int(item['nodeb']),
                        'srcIfName': item['inta']['ifname'],
                        'tgtIfName': item['intb']['ifname'],
                        'srcDevice': int(item['nodea']),
                        'tgtDevice': int(item['nodeb'])
                    })                   
                return topology_dict
            else:
                return self.generate_full()                         
        else:
            return self.generate_full()

    def generate_full(self):
        topology_dict = {'nodes': [], 'links': []}
        for k,item in self.nodes.items():
            if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82']:
                name= f"ММТС-9 {item.get('host')}"
            elif item.get('ip') in ['217.76.46.100','217.76.46.127']:
                name = f"ASBR {item.get('host')}"
            elif item['type'] == 'cloud':
                name = item.get('name') if item.get('name') else item.get('location')
            else:
                name = item.get('host')            
            if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82']:
                icon = 'cloud'
            elif item.get('ip') in ['217.76.46.100','217.76.46.127']:
                icon = 'cloud'
            elif item.get('icon'):
                icon = item.get('icon')
            elif item['type'] == 'customer':
                icon = 'host'
            elif item['type'] == 'cloud':
                icon = 'cloud'
            else:
                icon = 'switch'
            color = 'blue'
            if k==1:
                color='orange'
            if item.get('devsegment') == 'Core':
                color='green'
                if item.get('location'):
                    name += " "+ item.get('location')
            topology_dict['nodes'].append({
                'id': int(item['id']),
                'name': name,
                'primaryIP': item.get('host') or item.get('ip'),
                'nazvanie': item.get('nazv'),
                'location': item.get('location'),
                'icon':  icon,
                'segment': item.get('devsegment'),
                'color': color,
                #'Открыть': '<a href=https://usrn.ccs.ru/oper/?core_section=device&action=device&type2=show&code='+str(item['id'])+'></a>'
            })
        for k,item in self.links.items():
            topology_dict['links'].append({
                'id': int(item['id']),
                'source': int(item['nodea']),
                'target': int(item['nodeb']),
                'linktext': item.get('linktext') if item.get('linktext') else '',
                #'srcIfName': item['inta']['ifname'],
                #'tgtIfName': item['intb']['ifname'],
                'srcDevice': self.nodes[item['nodea']]['name'] + " . " + str(item['inta']['ifname']), #int(item['nodea']),
                'tgtDevice': self.nodes[item['nodeb']]['name'] + " . " + str(item['intb']['ifname']) #int(item['nodeb']),
            })   
        edge_labels={}
        G = nx.Graph()
        for v in topology_dict['nodes']:
            G.add_node(v['id'])
        for item in topology_dict['links']:
            G.add_edge(item['source'], item['target'])
        pos =  nx.spring_layout(G)
        asbrid = 0
        for i in topology_dict['nodes']:
            if i['primaryIP'] == '217.76.46.100':
                asbrid = i['id']
        if asbrid != 0:
            path = nx.shortest_path(G,source=topology_dict['nodes'][0]['id'],target=asbrid)
            path_edges = list(zip(path,path[1:]))
            for x in topology_dict['links']:
                for i in path_edges:
                    if x['source'] in i and x['target'] in i:
                        x['color'] = 'green'
            for x in topology_dict['nodes']:
                for i in path_edges:
                    if x['id'] in i :
                        x['color'] = 'green'
        return topology_dict

class DeviceMapfResponse(BaseModel):
    result: List[Dict]

class DeviceMapRequest(BaseModel):
    device_id: int
    with_noc: Optional[int] = 0
    to_core: Optional[int] = 0
 
class DeviceMapAPI(NBIAPI):
    api_name = "customermap"
    openapi_tags = ["customermap API"]
    usurl="http://usrn.ccs.ru/api.php?key=weifdovIpyirdyilyablichhyasgojyatwejIkKenvaitnajal"
    rnusurl="http://usrn.ccs.ru/rnapi.php?key=weifdovIpyirdyilyablichhyasgojyatwejIkKenvaitnajal"
    profiles = []
    count=0
    with_noc = 0
    to_core = 0
    def get_routes(self):
        route_post ={
            "path": "/api/nbi/devicemap",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "devicemap",
            "description": ""
        }
        return [route_post]
    def nocgetlinks(self, topoinfo, moip,with_noc, to_core):
        if not self.profiles:
            iprofiles = InterfaceProfile.objects.filter(name__contains='Uplink')
            iprofiles2 = InterfaceProfile.objects.filter(name__contains='Core')
            self.profiles = [x for x in iprofiles] + [x for x in iprofiles2]
        MOs = ManagedObject.objects.filter(address=moip)
        if MOs:
            cur_mo = MOs[0]
        else:
            return 0
        mo_links=[]
        if  to_core==1 and (re.findall(r"[C,c]ore", cur_mo.segment.name) or re.findall(r"G.8032", cur_mo.segment.name) or re.findall(r"[C,c]ore", cur_mo.administrative_domain.name)):
            return 0
        moid = cur_mo.id
        cur_nodeid = topoinfo.findnode_id_byip(cur_mo.address)
        if cur_nodeid==0:
            cur_nodeid = topoinfo.newNOCnode(cur_mo)
        mo_alllinks = Link.objects.filter(linked_objects__in=[moid])
        mointerfaces= Interface.objects.filter(managed_object__in=[moid], profile__in=[x.id for x in self.profiles])
        for i in mointerfaces:
            for l in mo_alllinks:
                if not i.id in l.interface_ids:
                    continue
                if l.interfaces[0].managed_object.address in topoinfo.hideip or l.interfaces[1].managed_object.address in topoinfo.hideip:
                    continue
                node_id_map=0
                if i.id == l.interfaces[0].id:
                    next_nodeid = topoinfo.newNOCnode(l.interfaces[1].managed_object)
                    nextmo = l.interfaces[1].managed_object
                    deva = cur_nodeid
                    devb = next_nodeid                    
                else:
                    next_nodeid = topoinfo.newNOCnode(l.interfaces[0].managed_object)
                    nextmo = l.interfaces[0].managed_object
                    devb = cur_nodeid
                    deva = next_nodeid                    
                inta = {'ifIndex': l.interfaces[0].ifindex,'ifName': l.interfaces[0].name}
                intb = {'ifIndex': l.interfaces[1].ifindex,'ifName': l.interfaces[1].name}
                newlinkid = topoinfo.newNOClink(deva, devb, inta, intb)   
                if newlinkid==0:
                    continue
                if to_core==1 and (re.findall(r"[C,c]ore", nextmo.segment.name) or re.findall(r"G.8032", nextmo.segment.name) or re.findall(r"[C,c]ore", nextmo.administrative_domain.name)):
                    topoinfo.nodes[next_nodeid]['devsegment'] = 'Core'
                    continue
                if (nextmo.address!='217.76.46.100'):
                    self.nocgetlinks(topoinfo, nextmo.address,with_noc, to_core)
        return 0

    def asknoc(self,topoinfo,with_noc, to_core):
        cur_nodelist = [x for x in topoinfo.nodes]
        for node in cur_nodelist:
            self.nocgetlinks(topoinfo, topoinfo.nodes[node].get('ip'),with_noc, to_core)

    #Ищет данные устройства в Userside по ID
    def get_usdevice_by_id(self, dev_type, device_id):
        result = {}
        if dev_type == 'system_device': 
            devtype = 'all'
        else:
            devtype = dev_type
        if device_id:
            response = requests.get(f"{self.usurl}+&cat=device&action=get_data&object_type={devtype}&object_id={device_id}")
            if(response.ok):
                data = json.loads(response.content)
                if data['Result'] == 'OK':
                    for i in data['data']:
                        result = data['data'][i]
        return result

    def get_usdevice_commutation(self, devtype=None, device_id=None):
        result = {}
        if device_id:
            response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type={devtype}&object_id={device_id}")
            if(response.ok):
                data = json.loads(response.content)
                if data['Result'] == 'OK':
                    result = data['data']
        return result
    
    def get_route(self, node,downlinks=0):
        result={}
        if downlinks == 1:
            target_int=node.get('downlink_interfaces')        
        else:
            target_int=node.get('uplink_interfaces')
        for k in target_int:
            response = requests.get(f"{self.rnusurl}&cat=rncommutation&action=route&type5={node['devtyper']}&code={node['device_id']}&port={k}")
            if(response.ok):
                data = json.loads(response.content)
                if data['data'] and len(data['data'])>1:
                    lastitem=data['data'][len(data['data'])-1][0]
                    if lastitem['objectType'] in usdevtypes:
                        if len(data['data'])>2: #lastitem['objectType'] == ussysdevtype and 
                            previtem=data['data'][len(data['data'])-2][0]
                            if previtem.get('clopis'):
                                linktext=previtem.get('clopis')
                            else:
                                linktext=''
                        else:
                            linktext=''
                        result[k]=[{'object_type': usdevtypes[lastitem['objectType']],
                                          'object_id': lastitem['objectId'],
                                          'direction': lastitem['objectSide'],
                                          'interface': lastitem['objectPort'],
                                          'comment': lastitem['comment'],
                                          'connect_id': lastitem['id'],
                                          'linktext': linktext
                                           }
                                          ]

        return result
    def get_links(self, topoinfo, cur_dev_type, cur_device_ip,with_noc, to_core,downlinks=0):
        cur_node = topoinfo.nodes.get(topoinfo.findnode_id_byip(cur_device_ip))
        if downlinks == 1:
            target_int=cur_node.get('downlink_interfaces')
        else:
            target_int=cur_node.get('uplink_interfaces')
        commutations = self.get_usdevice_commutation(cur_dev_type, cur_node['device_id'])
        self.temp1 = downlinks
        nodata=True
        for k in commutations:
            if (target_int and k in target_int):
                for item in commutations[k]:
                    if item['object_type']=='switch' or item['object_type']=='radio':
                        nodata=False
        if nodata and target_int:
            commutations = self.get_route(cur_node,downlinks)
        if commutations and cur_node:
            #Перебираем соединения, если интерфейс устройства на имеет признак Uplink переходим к следующему интерфейсу
            for cur_device_interface in commutations:
                if not cur_device_interface in target_int:
                    continue
                #Цикл по списку коммутаций интерфейса
                for item in commutations[cur_device_interface]:
                    if item['object_type']=='switch' or item['object_type']=='radio'  or item['object_type'] == 'system_device':
                        cid = item.get('connect_id')
                    #Проверяем наличие устройства с которым скоммутирован интерфейс в списке устройств
                        newnodeid = topoinfo.findnode_by_device_id(item['object_id'],'userside')
                        if newnodeid != 0 :
                            nextdev = topoinfo.nodes[newnodeid]
                            devdata = self.get_usdevice_by_id(item['object_type'], item['object_id']) 
                        #если его нет создаем
                        else:    
                            devdata = self.get_usdevice_by_id(item['object_type'], item['object_id'])  
                            if devdata.get('host') and devdata['host'] in topoinfo.hideip:
                                continue          
                            devdata['linktext'] = item.get('linktext') if item.get('linktext') else ''
                            nextnodeid = topoinfo.newUSnode(devdata)  
                            nextdev =  topoinfo.nodes[nextnodeid]     
                        ifnum =  item.get('interface')
                        #Создать линк
                        deva = cur_node
                        devb = nextdev
                        inta = cur_node['interfaces'][str(cur_device_interface)]
                        intb = nextdev['interfaces'][str(ifnum)]
                        newlinkid = topoinfo.newUSlink(deva, devb, inta, intb,cid)   
                        if newlinkid==0:
                            continue
                        if downlinks == 1:
                            continue
                        if   to_core==1 and ((devdata and devdata.get('additional_data') and devdata['additional_data'].get('26') in ['G.8032', 'core', 'core-ring'])):
                            nextdev['devsegment'] = 'Core'
                            continue
                        if (nextdev['ip'] and nextdev['ip']!='217.76.46.100'):
                            self.get_links(topoinfo, item['object_type'], nextdev['ip'],with_noc, to_core)

    def go(self, device_id, with_noc, to_core):
        topoinfo = TopologyInfo()
        self.t = topoinfo
        topoinfo.nodes={}
        topoinfo.links={}
        topoinfo.node_id_map = []
        topoinfo.link_id_map = []
        devdata = self.get_usdevice_by_id('all', device_id)
        nextnodeid = topoinfo.newUSnode(devdata)  
        nextdev =  topoinfo.nodes[nextnodeid]  
        if (nextdev['ip']!='217.76.46.108' and nextdev['ip']!='217.76.46.119' and nextdev['ip']!='10.76.33.82'):
            self.get_links(topoinfo,nextdev['dtype'], nextdev['ip'],with_noc, to_core)
            if devdata.get('dnlink_iface_array'):
                self.get_links(topoinfo,nextdev['dtype'], nextdev['ip'],with_noc, to_core,1)
        else:
            result={'Result':'Fail', 'message': 'Fail request customer commutation'}
            return result
        if with_noc:
            self.asknoc(topoinfo,with_noc, to_core)
        return {'Result': 'Ok', 'data':topoinfo.generatejs(to_core)}

    async def handler(self, req:DeviceMapRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        result = {}
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        connect()
        device_id=req.device_id
        with_noc = req.with_noc
        to_core = req.to_core
        result = self.go(device_id,with_noc, to_core)
        if result['Result'] == 'Ok':
            return JSONResponse(content=result['data'], media_type="application/json")
        else:
            topoinfo = None
            return JSONResponse(content={'nodes':{},'links':{}}, media_type="application/json")

# Install router
DeviceMapAPI(router)