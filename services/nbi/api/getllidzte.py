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
import tornado.gen
import ujson
import six
import re

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

Request = DictParameter(
    attrs={
        "host": StringParameter(required=True),
        "port": StringParameter(required=True),
        "sn": StringParameter(required=True),
    }
)


class GetllidzteAPI(NBIAPI):
    name = "getllidzte"

    @authenticated
    @tornado.gen.coroutine
    def post(self):
        connect()
        code, result = yield self.executor.submit(self.handler)
        self.set_status(code)
        if isinstance(result, six.string_types):
            self.write(result)
        else:
            self.write(ujson.dumps(result))

    def handler(self):
        # Decode request
        try:
            req = ujson.loads(self.request.body)
        except ValueError:
            return 400, "Cannot decode JSON"
        # Validate
        try:
            req = Request.clean(req)
        except ValueError as e:
            return 400, "Bad request: %s" % e
        host = str(req["host"])
        port = str(req["port"])
        sn = str(req["sn"])
        mo = ManagedObject.objects.get(address = host)
        if not mo:
           return 404, "MO not found"
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
        return 200, data

