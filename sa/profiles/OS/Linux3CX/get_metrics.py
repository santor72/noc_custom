# ---------------------------------------------------------------------
# 3CX.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from noc.core.mongo.connection import connect


# NOC modules
from noc.core.text import parse_kv
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from noc.sa.models.managedobject import ManagedObject

from noc.custom.lib.cx import obj3CX

class Script(GetMetricsScript):
#    def execute(self, metrics):
#        self.logger.debug('Yesssssssssssssssssssss')

    @metrics([
                  'Telephony | SIP | Sessions | Active'
            ],
        access=None,
        volatile=True,
    )
    def collect_telephony_metrics(self, metrics):
        connect()
        ipaddress = self.credentials.get('address')
        mo = ManagedObject.objects.filter(address=ipaddress)
        cxuser = mo[0].get_attr('apiuser')
        cxpasswd = mo[0].get_attr('apipasswd')
        cxurl = mo[0].get_attr('apiurl')
        cx = obj3CX(user=cxuser,passwd=cxpasswd, url=cxurl)
        cx.login()
        r = cx.active_calls()
        if not r['failed']:
            c = len(r['result'])
        else:
            c = None
        self.set_metric(id=("Telephony | SIP | Sessions | Active", None), value=c, path=[])
        cx.logout()


