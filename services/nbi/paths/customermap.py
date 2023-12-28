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

    def generate_link_id(self,ip1,ifnum1,ip2,ifnum2):
        if ip1 > ip2:
            idstr=f"{ip2}-{ifnum2}-{ip1}-{ifnum1}"
        elif ip1 < ip2:
            idstr=f"{ip1}-{ifnum1}-{ip2}-{ifnum2}"
        return idstr

    def generate_node_id(self,ipstr='1.1.1.1'):
        ip = netaddr.IPAddress(ipstr)
        return ip.value

    def getnode(self, dev_type, dev_id):
        response = requests.get(f"{self.usurl}+&cat=device&action=get_data&object_type={dev_type}&object_id={dev_id}")
        if(response.ok):
            data = json.loads(response.content)
            return data['data'].get(str(dev_id))
        else:
            return {}
    
    def get_links(self, dev_type, dev_id, nodes, links):
        #Получить списко коммутаций устойства
        response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type={dev_type}&object_id={nodes[dev_id]['id']}")
        if(response.ok):
            data = json.loads(response.content)
            if data['Result'] == 'OK':
                #Перебираем соединения, если интерфейс устройства на имеет признак Uplink переходим к следующему интерфейсу
                for k in data['data']:
                    if not k in nodes[dev_id].get('uplink_ifaces'):
                        continue
                    #Цикл по списку коммутаций интерфейса
                    for item in data['data'][k]:
                        #Проверяем наличие устройства с которым скоммутирован интерфейс в списке устройств nodes
                        if item['object_type']=='switch' or item['object_type']=='radio':
                            newnodeid = self.generate_node_id(item['host'])
                            if newnodeid in nodes:
                                devdata = nodes[newnodeid]
                                ifaces = devdata.get('ifaces')
                                uplink_ifaces = devdata.get('uplink_iface_array')
                            else:
                                devdata = self.getnode(item['object_type'], item['object_id'])                        
                                ifaces = devdata.get('ifaces')
                                uplink_ifaces = devdata.get('uplink_iface_array')
                                nodes[newnodeid] = {'id': item['object_id'],
                                                            'type':item['object_type'],
                                                            'nazv': devdata.get('nazv'),
                                                            'location': devdata.get('location'),
                                                            'uzelcode': devdata.get('uzelcode'),
                                                            'host': devdata.get('host'),
                                                            'ip': devdata.get('host'),
                                                            'ifaces': ifaces,
                                                            'uplink_ifaces': uplink_ifaces
                                                            }
                            ifnum =  item.get('interface')
                            #Создать id для линка
                            newlinkid = self.generate_link_id(dev_id,nodes[dev_id][k].get('ifIndex'),newnodeid,ifaces['ifnum']['ifIndex'])
                            if newlinkid in links:
                                continue
                            links[newlinkid]={
                                'id':item['connect_id'],
                                'nodea': nodes[dev_id].get('ip'),
                                'nodeb':item['host'],
                                'inta':nodes[dev_id]['ifaces'].get(k),
                                'intb': ifaces.get(str(ifnum))
                                }
                            if (devdata.get('host')!='217.76.46.108' and devdata.get('host')!='217.76.46.119' and devdata.get('host')!='10.76.33.82'):
                                self.get_links(item['object_type'], newnodeid, nodes, links)
    
    async def handler(self, req:CustomerMapRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        result = {}
        nodes={}
        links={}
        customer={}
        if not self.profiles:
            iprofiles = InterfaceProfile.objects.filter(name__contains='Uplink')
            iprofiles2 = InterfaceProfile.objects.filter(name__contains='Core')
            self.profiles = [x for x in iprofiles] + [x for x in iprofiles2]
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        connect()
        customer_id=req.customer_id
        a_response = requests.get(f"{self.usurl}&cat=customer&action=get_data&customer_id={customer_id}")
        if a_response.ok:
            customer=json.loads(a_response.content)
            if customer['Result'] != 'OK':
                result={'Result':'Fail', 'message': 'Customer not found'}
                return JSONResponse(content=result, media_type="application/json")
        else:
            result={'Result':'Fail', 'message': 'Customer find error'}
            return JSONResponse(content=result, media_type="application/json")
        nodes[customer_id] = {}
        nodes[customer_id] = {'id': customer_id, 
                      'type': 'customer',
                      'host':customer['Data']['login'],
                      'ip': customer['Data']['ip_mac'],
                      'location': customer['Data']['login'],
                      'nazv': customer['Data']['login']
                     }
        ac_response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type=customer&object_id={customer_id}")
        if(ac_response.ok):
            ac_data = json.loads(ac_response.content)
            if ac_data['Result'] == 'OK':
                for ac_item in ac_data['data']:
                    if ac_item['object_type']=='switch' or ac_item['object_type']=='radio':
                        devdata = self.getnode(ac_item['object_type'], ac_item['object_id'])
                        ifnum =  ac_item.get('interface')
                        ifaces = devdata.get('ifaces')
                        uplink_ifaces = [x for x in devdata.get('uplink_iface_array')]
                        ifname=''
                        if ifnum:
                            if ifaces.get(ifnum):
                                ifname = ifaces[ifnum].get('ifName')
                        links[ac_item['connect_id']]={'id':ac_item['connect_id'], 'nodea': customer_id,'inta':{'ifIndex': 1,
                                                                                                            'ifType': 1,
                                                                                                            'ifName': 'C',
                                                                                                            'ifNumber': 1},
                                                    'nodeb':ac_item['object_id'], 'intb': ifaces.get(str(ifnum))}
                        newnodeid = self.generate_node_id(devdata.get('host'))
                        nodes[newnodeid] = {'id': ac_item['object_id'],
                                                    'type':ac_item['object_type'],
                                                    'nazv': devdata.get('nazv'),
                                                    'location': devdata.get('location'),
                                                    'uzelcode': devdata.get('uzelcode'),
                                                    'host': devdata.get('host'),
                                                    'ip': devdata.get('host'),
                                                    'ifaces': ifaces,
                                                    'uplink_ifaces': uplink_ifaces
                                                    }
                        self.get_links(ac_item['object_type'], newnodeid, nodes, links)
            else:
                result={'Result':'Fail', 'message': 'Fail find customer commutation'}
                return JSONResponse(content=result, media_type="application/json")                                        
        else:
            result={'Result':'Fail', 'message': 'Fail request customer commutation'}
            return JSONResponse(content=result, media_type="application/json")  
        topology_dict = {'nodes': [], 'links': []}
        for k,item in nodes.items():
            topology_dict['nodes'].append({
                'id': int(item['id']),
                'name': 'MSK-IX' if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82'] else item.get('host'),
                'primaryIP': item.get('host') or item.get('ip'),
                'nazvanie': item.get('nazv'),
                'location': item.get('location'),
                'icon': 'host' if item['type'] == 'customer' else ('cloud' if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82'] else 'switch')
            })
        for k,item in links.items():
            topology_dict['links'].append({
                'id': int(item['id']),
                'source': int(item['nodea']),
                'target': int(item['nodeb']),
                'srcIfName': item['inta']['ifName'],
                'tgtIfName': item['intb']['ifName'],
                'srcDevice': int(item['nodea']),
                'tgtDevice': int(item['nodeb'])
            })                          
        result=topology_dict
        return JSONResponse(content=result, media_type="application/json")

# Install router
CustomerMapAPI(router)