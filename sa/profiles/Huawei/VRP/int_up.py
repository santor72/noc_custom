# ---------------------------------------------------------------------
# Huawei.VRP.add_vlan
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.iaddvlan import IAddVlan


class Script(BaseScript):
    name = "Huawei.VRP.int_down"
    interface = IIntDown

    def execute(self, ifname):
        with self.configure():
            self.cli("interface %s" % ifname)
            self.cli("undo shutdown")
            self.cli("quit")
        self.save_config()
        return True
