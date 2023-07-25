# ---------------------------------------------------------------------
# BDCOM.xPON.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.text import parse_table
from noc.core.mac import MAC


class Script(BaseScript):
    name = "BDCOM.xPON.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if mac is not None:
            cmd += " %s" % MAC(mac).to_cisco()
        r = []
        res_getmac=self.cli(cmd)
        for item in res_getmac.split('\n'):
            if re.findall("epon(\d+)/(\d+):\d",item):
                newrec=item
                newrec=re.sub("\s+","\t",newrec)
                newrec=re.sub("epon(\d+)/(\d+):\d+","EPON"+r'\1'+'/'+r"\2",newrec)
                i = newrec.split('\t')
                r += [{"vlan_id": i[0], "mac": i[1], "interfaces": [i[3]], "type": "D"}]
        return r
