# ---------------------------------------------------------------------
# ZTE.ZXA10-1-2.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "ZTE.ZXA10-1-2.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^\s*(?:out|in)band mac: (?P<inmac>\S+)\s*\n"
        r"^\s*(?:outband|base) mac\s*: (?P<outmac>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        macs = []
        v = self.cli("show mac system", cached=True)
        match = self.rx_mac.search(v)
        macs = sorted([match.group("inmac"), match.group("outmac")])
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
