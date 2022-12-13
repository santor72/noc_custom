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
from pydantic import BaseModel
from fastapi.responses import JSONResponse

# NOC modules
from noc.sa.models.action import Action
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE
from noc.core.validators import is_ipv4

router = APIRouter()

class ShowRequest(BaseModel):
    ip: str
    cmd: str

class ShowgResponse(BaseModel):
    result: str
    
class Show(NBIAPI):
    api_name = "zteregonu"

    def get_routes(self):
        route = {
            "path": "/api/nbi/show",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "show",
            "description": "run show command",
        }
        return [route]
    async def handler(self, req: ShowRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        if not is_ipv4(req.ip):
            raise HTTPException(400, "Bad request: no ip address")
        connect()
        mo = ManagedObject.objects.get(address = req.ip)
        if not mo:
            raise HTTPException(404, "Bad request: no MO found")
        data = mo.scripts.commands(commands = [req.cmd])
        return JSONResponse(content=data, media_type="application/json")

# Install router
Show(router)