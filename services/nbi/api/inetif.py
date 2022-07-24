# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# config API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import time
import os
import json

# Third-party modules
import tornado.gen

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.mongo.connection import connect
from noc.services.nbi.base import NBIAPI
# Third-party modules
from tornado.ioloop import IOLoop
import tornado.queues

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_ipv4
from noc.core.ioloop.ping import Ping
from noc.config import config
class InetIfAPI(NBIAPI):
    name = "inetif"

    @authenticated
    @tornado.gen.coroutine
    def get(self):
        code, result = yield self.executor.submit(self.handler)
        self.set_status(code)
        self.set_header("Content-Type", "application/json")
        if code != 204:
            self.write(result)

    def handler(self):
        try:
            connect()
            result=[]
            iprofiles = InterfaceProfile.objects.filter(name__contains='Uplink-Inet')
            inetint = Interface.objects.filter(profile__in=[x.id for x in iprofiles])
            for item in inetint:
                name=f"{item.managed_object.name} {item.description}({item.name})"
                bi_id = item.managed_object.bi_id
                path = item.name
                result.append(f"{name}:{bi_id};{path}")
            return 200, json.dumps(result)
        except ValueError:
            return 400, "Cannot decode JSON"


    @classmethod
    def get_path(cls):
        return r"%s" % cls.name, r"%s/(.+)" % cls.name, r"%s/(.+)/(.+)" % cls.name

