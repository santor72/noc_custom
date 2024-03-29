# ---------------------------------------------------------------------
# Qtech.QSW2800.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript
from .oidrules.slot import SlotRule
from .oidrules.enterprise import EnterpriseRule


class Script(GetMetricsScript):
    name = "Qtech.QSW2800.get_metrics"

    OID_RULES = [SlotRule, EnterpriseRule]
    @metrics(
         [
             "Interface | DOM | RxPower",
             "Interface | DOM | Temperature",
             "Interface | DOM | TxPower",
             "Interface | DOM | Voltage",
         ],
         has_capability="DB | Interfaces",
         has_script="get_dom_status",
         access="C",  # CLI version
         volatile=False,
    )
    def collect_dom_metrics(self, metrics):
         r = {}
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
         return r

