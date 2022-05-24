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
        "action": StringParameter(required=True),
        "host": StringParameter(required=True),
        "port": StringParameter(required=True),
        "sn": StringParameter(required=True),
        "llid": IntParameter(required=True),
        "login": StringParameter(required=True),
        "passwd": StringParameter(required=True),
        "vlanid": StringParameter(required=True)
    }
)


class ZTERegONU(NBIAPI):
    name = "zteregonu"

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
        actionoutput=["Result is"]
        output=["Result is"]
        hostip = str(req["host"])
        mo = ManagedObject.objects.get(address = hostip)
        if not mo:
           return 404, "MO not found"
        vlanid = mo.get_attr('pppoevlan')
        actionname = str(req["action"])
        data = {'port': str(req["port"]),
                'sn': str(req["sn"]),
                'llid': int(req["llid"]),
                'login': str(req["login"]),
                'passwd': str(req["passwd"]),
                'vlanid': str(req["vlanid"])
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
        return 200, actionoutput

