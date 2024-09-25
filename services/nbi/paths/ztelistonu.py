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
from noc.inv.models.interface import Interface
from noc.core.mongo.connection import connect
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE
from typing import Dict

router = APIRouter()

class ZTEListONURequest(BaseModel):
    ip: str

class ZTEListONU(NBIAPI):
    api_name = "/api/nbi/ztelistonu"

    def get_routes(self):
        route = {
            "path": "/api/nbi/ztelistonu",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "zteregonu",
            "description": "ztelistonu",
        }
        return [route]
    async def handler(self, req: ZTEListONURequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        # Decode request
        hostip = req.ip
        mo = ManagedObject.objects.get(address = hostip)
        i = Interface.objects.filter(managed_object = mo)
        cmd = [f"show gpon onu baseinfo  {x.name}" for x in i if re.findall(r'gpon-olt', x.name)]
        params={"commands":cmd, "ignore_cli_errors":True}
        result = mo.scripts.commands(**params)         
        return JSONResponse(content=result, media_type="application/json")
        
# Install router
ZTEListONU(router)