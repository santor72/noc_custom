# Python modules
from __future__ import absolute_import
import time
import os
import sys
import json
import requests
import re
from typing import List, Union, Dict, Optional

# Third-party modules
from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# NOC modules
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class gUSDResponse(BaseModel):
    result: List[Dict]

class gUSDAPI(NBIAPI):
    api_name = "getusdevices"
    openapi_tags = ["get US devices API"]
    usurl="http://usrn.ccs.ru//api.php?key=weifdovIpyirdyilyablichhyasgojyatwejIkKenvaitnajal"
    features=[]
    def get_routes(self):
        route_post ={
            "path": "/api/nbi/getusdevices",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "getusdevices",
            "description": ""
        }
        return [route_post]
    def getuzel(id):
        response = requests.get(usurl+"&cat=node&action=get&id=" + str(id))
        if(response.ok):
            data = json.loads(response.content.decode('utf-8'))
            return data['data'].get(str(id))
        else:
            return {}

    def getnode(dev_type, dev_id):
        response = requests.get(usurl+"&cat=device&action=get_data&object_type="+dev_type+"&object_id="+str(dev_id))
        if(response.ok):
            data = json.loads(response.content.decode('utf-8'))
            return data['data'].get(str(dev_id))
        else:
            return {}

    def getnodes(dev_type="switch"):
        response = requests.get(usurl+"&cat=device&action=get_data&object_type="+dev_type)
        if(response.ok):
            data = json.loads(response.content.decode('utf-8'))
            for k,v in data['data'].items():
                yield v
        else:
            return {}

    async def handler(self, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        result = {}
        dev_types=["switch", "olt", "radio"]
        for i in dev_types:
            for a in self.getnodes(i):
                if a.get('host') and a.get('uzelcode'):
                    b = self.getuzel(a.get('uzelcode'))
                if b and b.get('coordinates'):
                        devfeature = {
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [b["coordinates"]["lon"],b["coordinates"]["lat"]]
                            },
                            "properties": {
                                "id":a.get('code'),
                                "name":a.get('name'),
                                "location":a.get('location'),
                                "ip":a.get('host'),
                                "uzelcode": a.get('uzelcode'),
                                "is_online": 1,
        #                        "is_online": a.get('is_online'),
                                "hasalarm": 0,
                                "alarmtext":"",
                                "devtype":i,
                                "devtyper":a.get("devtyper")
                            }
                        }
                        features.append(devfeature)
                        if a.get('is_online')==0:
                            offline.append({"id":a.get('code'), "ip":a.get('host'), "type": a.get('devtyper'),"location":a.get('location')})
                else:
                    continue

        geoJson={
            "type": "FeatureCollection",
            "features": features,
        }

        return JSONResponse(content=geoJson, media_type="application/json")

# Install router
gUSDAPI(router)