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
from noc.main.models.customfieldenumvalue import CustomFieldEnumValue
from noc.main.models.customfieldenumgroup import CustomFieldEnumGroup
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
        "org": StringParameter(required=True),
    }
)


class GetoltAPI(NBIAPI):
    name = "getolt"

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
        org = str(req["org"])
        enumgroup=CustomFieldEnumGroup.objects.filter(name=org);
        enumvalues=CustomFieldEnumValue.objects.filter(enum_group=enumgroup[0])
        if not enumgroup:
           return 404, "MO not found"
        data = {}
        for i in enumvalues:
            data.update({i.key:i.value})
        return 200, data

