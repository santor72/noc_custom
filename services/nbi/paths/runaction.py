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
from typing import Dict

router = APIRouter()

class RunActionRequest(BaseModel):
    actname: str,
    ip: str,
    p: Dict

class RunAction(NBIAPI):
    api_name = "/api/nbi/runaction"

    def get_routes(self):
        route = {
            "path": "/api/nbi/runaction",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "zteregonu",
            "description": "runaction",
        }
        return [route]
    async def handler(self, req: RunActionRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        # Decode request
        hostip = req.ip
        mo = ManagedObject.objects.get(address = hostip)
        actname = req.actname
        params = req.p
        result = params
        action = Action.objects.get(name=actname)
        data = {x.name:'' for x in action.params}
        for k,v in p.items():
            data[k] = v
        cmd = str(action.expand(mo,**data))
        params={"commands":cmd.split('\n'), "ignore_cli_errors":True}
        result = mo.scripts.commands(**params)
        return JSONResponse(content=result, media_type="application/json")
        
# Install router
RunAction(router)