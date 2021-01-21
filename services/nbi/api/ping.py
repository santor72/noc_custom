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
from noc.sa.models.managedobject import ManagedObject
from noc.services.nbi.base import NBIAPI
# Third-party modules
from tornado.ioloop import IOLoop
import tornado.queues

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.validators import is_ipv4
from noc.core.ioloop.ping import Ping
from noc.config import config


class PingAPI(NBIAPI):
    name = "ping"

    @authenticated
    @tornado.gen.coroutine
    def get(self, ip):
        code, result = yield self.executor.submit(self.handler, ip)
        self.set_status(code)
        self.set_header("Content-Type", "text/plain")
        if code != 204:
            self.write(result)

    def handler(self, ip):
        if is_ipv4(ip):
           return 200, json.dumps(self.doping(ip));
        else:
           try:
               req = json.loads(self.request.body)
               r = []
               for n in req:
                   if is_ipv4(n):
                      r.append(self.doping(ip))
                   return 200, json.dumps(r)
           except ValueError:
               return 400, "Cannot decode JSON"

    def doping(self, ip):
        if is_ipv4(ip):
           if os.system('ping -c 2 -W 1 %s > /dev/null'%ip) == 0:
             return {ip : 'Up'};
           else:
             return {ip : 'Down'};
    
    
    @classmethod
    def get_path(cls):
        return r"%s" % cls.name, r"%s/(.+)" % cls.name, r"%s/(.+)/(.+)" % cls.name

