# ---------------------------------------------------------------------
# Huawei.VRP.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus
from noc.core.text import parse_table, parse_kv


class Script(BaseScript):
    name = "NAG.SNR.get_dom_status"
    interface = IGetDOMStatus

    rx_port = re.compile(r"Port (?P<port>\S+\d+) transceiver diagnostic information:")

    def execute(self, interface=None):
        cmd = "show transceiver"
        if interface is not None:
            cmd += " interface  %s" % interface
        try:
            c = self.cli(cmd)
        except self.CLISyntaxError:
            return []
        r = []
        for s in c.split("\n"):
            match = re.match(r"^\d",s)
            if match:
             try:
                i = s.split()
                iface = {"interface": "Ethernet"+i[0]}
                iface["optical_tx_dbm"] = float(i[5])
                iface["optical_rx_dbm"] = float(i[4])
                iface["current_ma"] = float(i[3])
                iface["temp_c"] = float(i[1])
                iface["voltage_v"] = float(i[2])
                r += [iface]
             except:
               raise
        return r
