# Python modules
from __future__ import absolute_import
import time
import os
import json
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
    nodes={}
    links={}
    customer={}

    def get_routes(self):
        route_get = {
            "path": "/api/nbi/customermap",
            "method": "GET",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "customermap",
            "description": "",
            }
        route_post ={
            "path": "/api/nbi/inetif",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "customermap",
            "description": ""
        }
        return [route_get, route_post]

    def getnode(self, dev_type, dev_id):
        response = requests.get(f"{usurl}+&cat=device&action=get_data&object_type={dev_type}&object_id={dev_id}")
        if(response.ok):
            data = json.loads(response.content)
            return data['data'].get(str(dev_id))
        else:
            return {}
    
    def get_links(self, dev_type, dev_id):
        response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type={dev_type}&object_id={dev_id}")
        if(response.ok):
            data = json.loads(response.content)
            if data['Result'] == 'OK':
                for k in data['data']:
                    if not k in nodes[dev_id].get('uplink_ifaces'):
                        continue
                    for item in data['data'][k]:
                        if item['connect_id'] in links:
                            continue
                        if item['object_type']=='switch' or item['object_type']=='radio':
                            if item['object_id'] in self.nodes:
                                devdata = nodes[item['object_id']]
                                ifaces = devdata.get('ifaces')
                                uplink_ifaces = devdata.get('uplink_iface_array')
                            else:
                                devdata = getnode(item['object_type'], item['object_id'])                        
                                ifaces = devdata.get('ifaces')
                                uplink_ifaces = devdata.get('uplink_iface_array')
                                self.nodes[item['object_id']] = {'id': item['object_id'],
                                                            'type':item['object_type'],
                                                            'nazv': devdata.get('nazv'),
                                                            'location': devdata.get('location'),
                                                            'uzelcode': devdata.get('uzelcode'),
                                                            'host': devdata.get('host'),
                                                            'ifaces': ifaces,
                                                            'uplink_ifaces': uplink_ifaces
                                                            }
                            ifnum =  item.get('interface')
                            self.links[item['connect_id']]={
                                'id':item['connect_id'],
                                'nodea': dev_id,
                                'nodeb':item['object_id'],
                                'inta':self.nodes[dev_id]['ifaces'].get(k),
                                'intb': ifaces.get(str(ifnum))
                                }
                            if (devdata.get('host')!='217.76.46.108' and devdata.get('host')!='217.76.46.119' and devdata.get('host')!='10.76.33.82'):
                                get_links(item['object_type'], item['object_id'])
    
    async def handler(self, req:CustomerMapRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        result = {}

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
        result=customer['Data']
        return JSONResponse(content=result, media_type="application/json")

# Install router
ObjectInetifAPI(router)