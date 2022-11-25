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
import six
import re
from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# NOC modules
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()

class ZTERegONURequest(BaseModel):
    host: str
    port: str
    sn: str
    action: str
    login: str
    passwd: str
    vlanid: str
#    model: str
    llid: int

    
class ZTERegONU(NBIAPI):
    api_name = "zteregonu"

    def get_routes(self):
        route = {
            "path": "/api/nbi/zteregonu",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "zteregonu",
            "description": "Register ONU on ZTE olt",
        }
        return [route]
    async def handler(self, req: ZTERegONURequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        # Decode request
        actionoutput=["Result is"]
        output=["Result is"]
        hostip = req.host
        mo = ManagedObject.objects.get(address = hostip)
        if not mo:
           raise HTTPException(404, "MO not found")
        actionname = req.action
        data = {'port': req.port,
                'sn': req.sn,
                'llid': req.llid,
                'login': req.login,
                'passwd': req.passwd,
                'vlanid': req.vlanid
                }
#delete onu
        action = Action.objects.get(name='zteunregonu')
        cmd1 = str(action.expand(mo,**data))
        params={"commands":cmd1.split('\n'), "ignore_cli_errors":True}
        result = mo.scripts.commands(**params)
        actionoutput.append(result)
#register onu
        action = Action.objects.get(name=actionname)
        cmd2 = str(action.expand(mo,**data))
        params={"commands":cmd2.split('\n'), "ignore_cli_errors":True}
        result = mo.scripts.commands(**params)
        actionoutput.append(result)
#save config
        action = Action.objects.get(name='ztewrite')
        cmd3 = str(action.expand(mo))
        params={"commands":cmd3.split('\n'), "ignore_cli_errors":True}
        result = mo.scripts.commands(**params)
        actionoutput.append(result)

        cmd4 = ['show run interface gpon-olt_{}'.format(data['port']),
#                'show run interface gpon-onu_{}:{}'.format(data['port'],data['llid']),
#                'show onu running config gpon-onu_{}:{}'.format(data['port'],data['llid'])
               ]
        params={"commands":cmd4, "ignore_cli_errors":True}
        #result = mo.scripts.commands(**params)
        #output.append(result)
        return JSONResponse(content=actionoutput, media_type="application/json")

# Install router
ZTERegONU(router)