# Python modules
from __future__ import absolute_import
import time
import os
import json
import requests
import re
import netaddr
from typing import List, Union, Dict

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

class TopologyInfo:
    nodes={}
    links={}
    current_link_id = 1
    current_node_id = 1
    node_id_map = []
    link_id_map = []
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
        self.nodes[newid] = {
            'id': newid,
            'hash': self.generate_node_hash(devdata['host']),
            'system': 'userside',
            'type': 'device',
            'device_id': devdata['ID'],
            'host': devdata['host'],
            'ip': devdata['host'],
            'location': devdata['location'],
            'name': devdata['name'] or devdata['nazv'],
            'interfaces': devdata['ifaces'],
            'uplink_interfaces': devdata['uplink_iface_array']
        }
        self.node_id_map.append({'id':newid, 'hash': self.generate_node_hash(devdata['host'])})
        return newid

    def newUSlink(self,a,b, inta, intb):
        if a['type'] != 'customer':
            newlinkhash = self.generate_link_hash(a['ip'], b['ip'], inta['ifIndex'], intb['ifIndex'])
            if self.map_link_id(newlinkhash):
                return 0
        else:
            newlinkhash = f"c-1-{b['host']}-{intb['ifIndex']}"
        newlinkid=self.current_link_id
        self.current_link_id+=1
        self.links[newlinkid]={
            'id' : newlinkid,
            'hash': newlinkhash,
            'system': 'userside',
            'nodea': a['id'],
            'nodeb':b['id'],
            'inta':{'ifindex': inta['ifIndex'], 'ifname': inta['ifName']},
            'intb': {'ifindex': intb['ifIndex'], 'ifname': intb['ifName']}
            }
        self.node_id_map.append({'id':newlinkid, 'hash': newlinkhash})
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
        return idstr

    def generatejs(self):
        topology_dict = {'nodes': [], 'links': []}
        for k,item in self.nodes.items():
            topology_dict['nodes'].append({
                'id': int(item['id']),
                'name': 'ММТС-9' if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82'] else item.get('host'),
                'primaryIP': item.get('host') or item.get('ip'),
                'nazvanie': item.get('nazv'),
                'location': item.get('location'),
                'icon': 'host' if item['type'] == 'customer' else ('cloud' if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82'] else 'switch')
            })
        for k,item in self.links.items():
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

class CustomerMapfResponse(BaseModel):
    result: List[Dict]

class CustomerMapRequest(BaseModel):
    customer_id: int
 
class CustomerMapAPI(NBIAPI):
    api_name = "customermap"
    openapi_tags = ["customermap API"]
    usurl="http://usrn.ccs.ru//api.php?key=weifdovIpyirdyilyablichhyasgojyatwejIkKenvaitnajal"
    profiles = []
    def get_routes(self):
        route_post ={
            "path": "/api/nbi/customermap",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "customermap",
            "description": ""
        }
        return [route_post]

    #Ищет данные устройства в Userside по ID
    def get_usdevice_by_id(self, dev_type, device_id):
        result = {}
        if device_id:
            response = requests.get(f"{self.usurl}+&cat=device&action=get_data&object_type={dev_type}&object_id={device_id}")
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

    def get_links(self, topoinfo, cur_dev_type, cur_device_ip):
        cur_node = topoinfo.nodes.get(topoinfo.findnode_id_byip(cur_device_ip))
        commutations = self.get_usdevice_commutation(cur_dev_type, cur_node['device_id'])
        if commutations and cur_node:
            #Перебираем соединения, если интерфейс устройства на имеет признак Uplink переходим к следующему интерфейсу
            for cur_device_interface in commutations:
                if not cur_device_interface in cur_node.get('uplink_interfaces'):
                    continue
                #Цикл по списку коммутаций интерфейса
                for item in commutations[cur_device_interface]:
                    if item['object_type']=='switch' or item['object_type']=='radio':
                    #Проверяем наличие устройства с которым скоммутирован интерфейс в списке устройств
                        newnodeid = topoinfo.findnode_by_device_id(item['object_id'],'userside')
                        if newnodeid != 0 :
                            nextdev = topoinfo.nodes[newnodeid]
                        #если его нет создаем
                        else:    
                            devdata = self.get_usdevice_by_id(item['object_type'], item['object_id'])   
                            nextnodeid = topoinfo.newUSnode(devdata)  
                            nextdev =  topoinfo.nodes[nextnodeid]     
                        ifnum =  item.get('interface')
                        #Создать линк
                        deva = cur_node
                        devb = nextdev
                        inta = cur_node['interfaces'][str(cur_device_interface)]
                        intb = nextdev['interfaces'][str(ifnum)]
                        newlinkid = topoinfo.newUSlink(deva, devb, inta, intb)   
                        if newlinkid==0:
                            continue
                        if (nextdev['ip']!='217.76.46.108' and nextdev['ip']!='217.76.46.119' and nextdev['ip']!='10.76.33.82'):
                            self.get_links(topoinfo, item['object_type'], nextdev['ip'])

    def go(self, topoinfo, customer_id):
        topoinfo = TopologyInfo()
        a_response = requests.get(f"{self.usurl}&cat=customer&action=get_data&customer_id={customer_id}")
        if a_response.ok:
            customer=json.loads(a_response.content)
            if customer['Result'] != 'OK':
                result={'Result':'Fail', 'message': 'Customer not found'}
                return JSONResponse(content=result, media_type="application/json")
        else:
            result={'Result':'Fail', 'message': 'Customer find error'}
            return JSONResponse(content=result, media_type="application/json")
        topoinfo.nodes[topoinfo.current_node_id] = {'id': customer_id, 
                            'type': 'customer',
                            'host':customer['Data']['login'],
                            'ip': customer['Data']['ip_mac'],
                            'location': customer['Data']['login'],
                            'nazv': customer['Data']['login']
                            }
        cur_node = topoinfo.nodes[topoinfo.current_node_id]
        topoinfo.current_node_id+=1
        ac_response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type=customer&object_id={customer_id}")
        if(ac_response.ok):
            ac_data = json.loads(ac_response.content)
            if ac_data['Result'] == 'OK':
                for ac_item in ac_data['data']:
                    if ac_item['object_type']=='switch' or ac_item['object_type']=='radio':
                        devdata = self.get_usdevice_by_id(ac_item['object_type'], ac_item['object_id'])
                        nextnodeid = topoinfo.newUSnode(devdata)  
                        nextdev =  topoinfo.nodes[nextnodeid]  
                        deva = cur_node
                        devb = nextdev
                        inta = {'ifIndex': 1,'ifType': 1,'ifName': 'C','ifNumber': 1}
                        intb = nextdev['interfaces'][str(ac_item.get('interface'))]
                        topoinfo.newUSlink(deva, devb, inta, intb)   
                        if (nextdev['ip']!='217.76.46.108' and nextdev['ip']!='217.76.46.119' and nextdev['ip']!='10.76.33.82'):
                            self.get_links(topoinfo, ac_item['object_type'], nextdev['ip'])
            else:
                result={'Result':'Fail', 'message': 'Fail find customer commutation'}
                return result
        else:
            result={'Result':'Fail', 'message': 'Fail request customer commutation'}
            return result
        return {'Result': 'Ok', 'data':topoinfo}

    async def handler(self, req:CustomerMapRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        result = {}
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        connect()
        customer_id=req.customer_id
        
        result = self.go(customer_id)
        if result['Result'] == 'Ok':
            topology_dict = result['data'].generatejs()
            result=topology_dict
            return JSONResponse(content=result, media_type="application/json")
        else:
            topoinfo = None
            return JSONResponse(content={'nodes':{},'links':{}}, media_type="application/json")

# Install router
CustomerMapAPI(router)