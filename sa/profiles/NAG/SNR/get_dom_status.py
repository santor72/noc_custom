# ---------------------------------------------------------------------
# Cisco.IOS.get_dom_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdomstatus import IGetDOMStatus


class Script(BaseScript):
    name = "NAG.SNR.get_dom_status"
    interface = IGetDOMStatus
    rx_line = re.compile(
        r"^(?P<interface>\S+)\s+(?P<temp_c>\S+)(?:\s+(?P<voltage_v>\S+))?\s+(?P<current_ma>\S+)\s+(?P<optical_rx_dbm>\S+)\s+(?P<optical_tx_dbm>\S+)$"
    )
    rx_val = re.compile(r"^(?P<val>-*\d+\.*\d*)\S*")

    def execute(self, interface=None):
        cmd = "show transceiver | i /"
        if interface is not None:
            cmd = "show  transceiver interface %s| i /" % interface
        try:
            v = self.cli(cmd)
        except self.CLISyntaxError:
            return []

        r = []
        for l in v.split("\n"):
            self.logger.info("\n"+l+"\n")
            match = self.rx_line.match(l.strip())
            if not match:
                continue
            temp_c = match.group("temp_c")
            if temp_c == "N/A":
                temp_c = None
            else:
                temp_c=self.rx_val.search(temp_c).group('val')
            voltage_v = match.group("voltage_v")
            if voltage_v == "N/A":
                voltage_v = None
            else:
                voltage_v=self.rx_val.search(voltage_v).group('val')
            current_ma = match.group("current_ma")
            if current_ma == "N/A":
                current_ma = None
            else:
                current_ma=self.rx_val.search(current_ma).group('val')
            optical_rx_dbm = match.group("optical_rx_dbm")
            if optical_rx_dbm == "N/A":
                optical_rx_dbm = None
            else:
                optical_rx_dbm = self.rx_val.search(optical_rx_dbm).group('val')
            optical_tx_dbm = match.group("optical_tx_dbm")
            if optical_tx_dbm == "N/A":
                optical_tx_dbm = None
            else:
                optical_tx_dbm = self.rx_val.search(optical_tx_dbm).group('val')
            r += [
                {
                    "interface": match.group("interface"),
                    "temp_c": temp_c,
                    "voltage_v": voltage_v,
                    "current_ma": current_ma,
                    "optical_rx_dbm": optical_rx_dbm,
                    "optical_tx_dbm": optical_tx_dbm,
                }
            ]
        return r
