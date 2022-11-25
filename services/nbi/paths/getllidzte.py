# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# telemetry API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict

# Third-party modules
import ujson
import six
import re
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect

from noc.sa.interfaces.base import (
    DictParameter,
    DictListParameter,
    StringParameter,
    StringListParameter,
    IntParameter,
    ListOfParameter,
    ListParameter,
)
from noc.pm.models.metrictype import MetricType
from noc.services.nbi.base import NBIAPI

class GetllidzteRequest(BaseModel):
    "host": str
    "port": str
    "sn": str
    
class GetllidzteAPI(NBIAPI):
    api_name = "getllidzte"

    def get_routes(self):
        route = {
            "path": "/api/nbi/getllidzte",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "getllidzte",
            "description": "Get LLID for ZTE olt",
        }
        return [route]

    async def handler(self, req: GetllidzteRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        host = req.host
        port = req.port
        sn = req.sn
        mo = ManagedObject.objects.get(address = host)
        if not mo:
           raise HTTPException(404, "MO not found")
        onu_ids=[]
        new_onu_id=0
        c_onu_id=0
        l_onu_id=0
        onu_exist=0
#        addonucommands="conf t \n interface gpon-olt_"+port+'\n'
        cmd = [str('show run interface gpon-olt_'+port+'\n')]
        res = mo.scripts.commands(commands=cmd)
        for i in res['output'][0].split('\n'):
            r = re.search(r"^\s+onu (?P<llid>\d+) type.+sn (?P<sn>\S+)$",i)
            if r:
                onu_ids.append(r.group('llid'))
                l_onu_id = c_onu_id
                c_onu_id = int(r.group('llid'))
                if sn == r.group('sn'):
                    new_onu_id = c_onu_id
                    onu_exist = 1
                    break
                if l_onu_id+1 < c_onu_id:
                    new_onu_id = l_onu_id+1
                    break
        if new_onu_id == 0:
           new_onu_id = c_onu_id+1 
        data = [new_onu_id, onu_exist]
        return Response(content=data, media_type="application/json")

# Install router
GetllidzteAPI(router)