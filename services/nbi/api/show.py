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
        "cmd": StringParameter(required=True),
    }
)


class ShowAPI(NBIAPI):
    name = "show"

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
        cmd = str(req["cmd"])
        mo = ManagedObject.objects.get(address = host)
        if not mo:
           return 404, "MO not found"
        data = mo.scripts.commands(commands = [cmd])
        return 200, data

