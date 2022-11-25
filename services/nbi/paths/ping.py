# Python modules
import os
#from typing import List, Union

# Third-party modules
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

# NOC modules
from noc.sa.models.objectstatus import ObjectStatus
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class ObjectPingRequest(BaseModel):
    ip: str


class ObjectPingResponse(BaseModel):
    result: str

class ObjectPingAPI(NBIAPI):
    api_name = "ping"
    openapi_tags = ["ping API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/ping",
            "method": "GET",
            "endpoint": self.handler,
            "response_model": ObjectPingResponse,
            "name": "ping",
            "description": "Ping one Managed Objects.",
        }
        return [route]

    async def handler(self, req: ObjectStatusRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        if not is_ipv4(req.ip):
            raise HTTPException(400, "Bad request: no ip address")
        return {result: self.doping(req.ip)}

    def doping(self, ip):
        if os.system('ping -c 2 -W 1 %s > /dev/null'%ip) == 0:
            return {ip : 'Up'};
        else:
             return {ip : 'Down'};
