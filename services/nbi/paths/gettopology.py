# Python modules
import os
#from typing import List, Union

# Third-party modules
from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal

# NOC modules
from noc.sa.models.objectstatus import ObjectStatus
from noc.services.nbi.base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE
from noc.core.validators import is_ipv4
from noc.custom.lib.gettopology import create_topology

router = APIRouter()


FilterBy = Literal["admindomains", "segments", "labels", "monames", "ip"]
class TopologyRequest(BaseModel):
    by: FilterBy = Field(..., description="Тип фильтра для выборки ManagedObject")
    values: list[str] = Field(..., min_length=1, description="Значения фильтра")


class ObjectGetTopologyAPI(NBIAPI):
    api_name = "gettopolgy"
    openapi_tags = ["gettopology API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/gettopology",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": JSONResponse,
            "response_model": None,
            "name": "gettopology",
            "description": "Network topology for  Managed Objects.",
        }
        return [route]

    async def handler(self, req: TopologyRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        topojson = create_topology(req.by, req.values)
        return JSONResponse(content=topojson, media_type="application/json")

# Install router
ObjectGetTopologyAPI(router)


