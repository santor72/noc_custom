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

class GETONUINFORequest(BaseModel):
    ip: str
    port: str
    llid: str
    serial: str

class GETONUINFO(NBIAPI):
    api_name = "/api/nbi/getonuinfo"

    def get_routes(self):
        route = {
            "path": "/api/nbi/getonuinfo",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "zteregonu",
            "description": "getonuinfo",
        }
        return [route]
    async def handler(self, req: GETONUINFORequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        # Decode request
        hostip = req.ip
        mo = ManagedObject.objects.get(address = hostip)
        if not mo:
           raise HTTPException(404, "MO not found")
        action = Action.objects.get(name='getonuinfo')
        data={'serial': req.serial, 'llid':req.llid, 'port': req.port}
        cmd = str(action.expand(mo,**data))
        params={"commands":cmd.split('\n'), "ignore_cli_errors":True}
        result = mo.scripts.commands(**params)
        actionoutput.append(result)
        return JSONResponse(content=actionoutput, media_type="application/json")

# Install router
GETONUINFO(router)