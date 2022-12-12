# Python modules
from __future__ import absolute_import
import time
import os
import json
#from typing import List, Union

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


#class ObjectInetifRequest(BaseModel):
    

class ObjectInetifResponse(BaseModel):
    result: str

class ObjectInetifAPI(NBIAPI):
    api_name = "inetif"
    openapi_tags = ["inetif API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/inetif",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "inetifget",
            "description": "",
            "path": "/api/nbi/inetif",
            "method": "GET",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "inetifpost",
            "description": "",            
        }
        return [route]

    async def handler(self, req: None, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        connect()
        result=[]
        iprofiles = InterfaceProfile.objects.filter(name__contains='Uplink-Inet')
        inetint = Interface.objects.filter(profile__in=[x.id for x in iprofiles])
        for item in inetint:
            name=f"{item.managed_object.name} {item.description}({item.name})"
            bi_id = item.managed_object.bi_id
            path = item.name
            result.append(f"{name}:{bi_id};{path}")            
        return JSONResponse(content=result, media_type="application/json")


# Install router
ObjectPingAPI(router)
