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
class OltUplinksAPI(NBIAPI):
    name = "oltuplinks"

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
            selector_name = 'point-OLT'
            connect()
            selector = ManagedObjectSelector.objects.filter(name=selector_name)
            mo=selector[0].managed_objects
            iprofiles = InterfaceProfile.objects.filter(name__contains='Uplink')
            oltint = Interface.objects.filter(managed_object__in=[x.id for x in mo], profile__in=[x.id for x in iprofiles])
            result=[]
            for item in oltint:
                name=item.managed_object.name
                bi_id = item.managed_object.bi_id
                path = item.name
                result.append(f"{name}:{bi_id};{path}")
            return 200, json.dumps(result)
        except ValueError:
            return 400, "Cannot decode JSON"


    @classmethod
    def get_path(cls):
        return r"%s" % cls.name, r"%s/(.+)" % cls.name, r"%s/(.+)/(.+)" % cls.name

