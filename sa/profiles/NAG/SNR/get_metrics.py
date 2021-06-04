# ---------------------------------------------------------------------
# Cisco.IOS.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.text import parse_kv
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
import re

def convert_sensor(value,precession):
        return value/(10*precession)

class Script(GetMetricsScript):
    name = "NAG.SNR.get_metrics"
    @metrics(
            [
              "Interface | DOM | RxPower",
              "Interface | DOM | TxPower",
             ],
            has_capability="DB | Interfaces",
            #has_script="get_dom_status",
            access="S",  # CLI version
            volatile=False,
            )
        
    def collect_dom_metrics(self, metrics):
        """
        Returns collected dom  metrics in form
        :return:
        """
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.4.1.40418.7.100.30.1.1.17"]):
             if s != None and s != 'NULL':
                  ipath = ["", "", "", n]
                  self.set_metric(id=("Interface | DOM | RxPower", ipath), value=s)
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.4.1.40418.7.100.30.1.1.22"]):
             if s != None and s != 'NULL':
                  ipath = ["", "", "", n]
                  self.set_metric(id=("Interface | DOM | TxPower", ipath), value=s)
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.4.1.40418.7.100.30.1.1.2"]):
             if s != None and s != 'NULL':
                  ipath = ["", "", "", n]
                  self.set_metric(id=("Interface | DOM | Temperature", ipath), value=s)
        return
