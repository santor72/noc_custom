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
    name = "Qtech.QSW2800.get_metrics"
    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<temp_c>\S+)(?:\s+(?P<voltage_v>\S+))?\s+(?P<current_ma>\S+)\s+(?P<optical_rx_dbm>\S+)\s+(?P<optical_tx_dbm>\S+)$"
    )
    rx_val = re.compile(r"^(?P<val>-*\d+\.*\d*)\S*")
    def dombycli(self, metrics):
         self.logger.info("\n\n\nStarting to track DOM by CLI\n\n\n")
         for m in self.scripts.get_dom_status():
             ipath = ["", "", "", m["interface"]]
             if m.get("temp_c") is not None:
                 self.set_metric(id=("Interface | DOM | Temperature", ipath), value=m["temp_c"])
             if m.get("voltage_v") is not None:
                 self.set_metric(id=("Interface | DOM | Voltage", ipath), value=m["voltage_v"])
             if m.get("optical_rx_dbm") is not None:
                 self.set_metric(id=("Interface | DOM | RxPower", ipath), value=m["optical_rx_dbm"])
             if m.get("current_ma") is not None:
                 self.set_metric(id=("Interface | DOM | Bias Current", ipath), value=m["current_ma"])
             if m.get("optical_tx_dbm") is not None:
                 self.set_metric(id=("Interface | DOM | TxPower", ipath), value=m["optical_tx_dbm"])
         return

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
        c = 0
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.4.1.40418.7.100.30.1.1.17"]):
             if s != None and s != 'NULL':
                  ipath = ["", "", "", n]
                  self.set_metric(id=("Interface | DOM | RxPower", ipath), value=self.rx_val.search(s).group('val'))
                  c = 1
        if c == 0:
             self.dombycli(metrics)
             return
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.4.1.40418.7.100.30.1.1.22"]):
             if s != None and s != 'NULL':
                  ipath = ["", "", "", n]
                  self.set_metric(id=("Interface | DOM | TxPower", ipath), value=self.rx_val.search(s).group('val'))
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.2.2.1.2", "1.3.6.1.4.1.40418.7.100.30.1.1.2"]):
             if s != None and s != 'NULL':
                  ipath = ["", "", "", n]
                  self.set_metric(id=("Interface | DOM | Temperature", ipath), value=self.rx_val.search(s).group('val'))
        return
