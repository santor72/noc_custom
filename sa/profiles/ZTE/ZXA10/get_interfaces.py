# ---------------------------------------------------------------------
# ZTE.ZXA10.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
#from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript
# NOC modules
import re


class Script(BaseScript):
    name = "ZTE.ZXA10.get_interfaces"
    interface = IGetInterfaces
    TIMEOUT = 240

    type = {"GUSQ": "gei_", "VDWVD": "vdsl_", "SCXN": "gei_", "PRWGS": "", "SMXA":"gei_","GTGOG":"gpon-olt_","GTGOH":"gpon-olt_","GTGHG":"gpon-olt_","GTGOE":"gpon-olt_"}
    rx_iface = re.compile(
        r"^(?P<ifname>\S+) is (?P<admin_status>activate|deactivate|down|administratively down|up),\s*"
        r"line protocol is (?P<oper_status>down|up).+\n"
        r"^\s+Description is (?P<descr>.+)\n",
        re.MULTILINE,
    )
    rx_vlan = re.compile(
        r"^(?P<mode>access=0|trunk\>0|hybrid\>=0)\s+(?P<pvid>\d+).+\n"
        r"^UntaggedVlan:\s*\n"
        r"(^(?P<untagged>\d+)\s*\n)?"
        r"^TaggedVlan:\s*\n"
        r"(^(?P<tagged>[\d,]+)\s*\n)?",
        re.MULTILINE,
    )
    rx_pvc = re.compile(
        r"^\s+Pvc (?P<pvc_no>\d+):\s*\n"
        r"^\s+Admin Status\s+:\s*(?P<admin_status>enable|disable)\s*\n"
        r"^\s+VPI/VCI\s+:\s*(?P<vpi>\d+)/(?P<vci>\d+)\s*\n",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"^(?P<ifname>\S+)\s+AdminStatus is (?P<admin_status>up),\s+"
        r"PhyStatus is (?:up),\s+line protocol is (?P<oper_status>up)\s*\n"
        r"^\s+Internet address is (?P<ip>\S+)\s*\n"
        r"^\s+Broadcast address is .+\n"
        r"^\s+IP MTU is (?P<mtu>\d+) bytes\s*\n",
        re.MULTILINE,
    )
    rx_mac = re.compile(
        r"^\s+Description is (?P<descr>.+)\n^\s+MAC address is (?P<mac>\S+)\s*\n", re.MULTILINE
    )

    def get_ifindex_map(self):
        """
        Retrieve name -> ifindex map
        """
        m = {}
        if self.has_snmp():
            try:
                # IF-MIB::ifDescr
#                t = self.snmp.get_table(".1.3.6.1.2.1.31.1.1.1.1")
                t = self.scripts.get_ifindexes()
                return t
                print('aaaaaaa')
                print(t)
                for i in t:
                    if t[i].startswith("ControlEthernet"):
                        continue
                    #m[self.profile.convert_interface_name(t[i])] = i
                    m[t[i]] = i
            except self.snmp.TimeOutError:
                pass
        return m

    def execute_cli(self):
        interfaces = []
        ifindex = self.get_ifindex_map()
        print(ifindex)
        ports = self.profile.fill_ports(self)
        print(ports)
        for p in ports:
            if int(p["port"]) < 1 or p["realtype"] == "":
                continue
            if p["realtype"] in self.type:
               prefix = self.type[p["realtype"]]
            else:
               continue
            for i in range(int(p["port"])):
                ifname = "%s%s/%s/%s" % (prefix, p["shelf"], p["slot"], str(i + 1))
                try:
                   v = self.cli("show interface %s" % ifname)
                except:
                   ifname = "%s%s/%s/%s" % ("xgei_", p["shelf"], p["slot"], str(i + 1))
                   try:
                      v = self.cli("show interface %s" % ifname)
                   except:
                      continue
                match = self.rx_iface.search(v)
                admin_status = bool(match.group("admin_status") == "up")
                oper_status = bool(match.group("oper_status") == "up")
                descr = match.group("descr").strip()
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "subinterfaces": [],
                }
                if iface["name"] in ifindex:
                    iface["snmp_ifindex"] = ifindex[iface["name"]]
                if descr not in ["none", "none."]:
                    iface["description"] = descr
                if prefix == "xgei_":
                    v = self.cli("show vlan port %s" % ifname)
                    match = self.rx_vlan.search(v)
                    sub = {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"],
                    }
                    if match.group("untagged"):
                        sub["untagged_vlan"] = match.group("untagged")
                    if match.group("tagged"):
                        sub["tagged_vlans"] = self.expand_rangelist(match.group("tagged"))
                    iface["subinterfaces"] += [sub]
                if prefix == "gei_":
                    v = self.cli("show vlan port %s" % ifname)
                    match = self.rx_vlan.search(v)
                    sub = {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"],
                    }
                    if match.group("untagged"):
                        sub["untagged_vlan"] = match.group("untagged")
                    if match.group("tagged"):
                        sub["tagged_vlans"] = self.expand_rangelist(match.group("tagged"))
                    iface["subinterfaces"] += [sub]
                if prefix == "vdsl_":
                    for match in self.rx_pvc.finditer(v):
                        sub = {
                            "name": "%s.%s" % (ifname, match.group("pvc_no")),
                            "admin_status": match.group("admin_status") == "enable",
                            # "oper_status": oper_status  # need more examples
                            "enabled_afi": ["BRIDGE", "ATM"],
                            "vpi": match.group("vpi"),
                            "vci": match.group("vci"),
                        }
                        iface["subinterfaces"] += [sub]
                interfaces += [iface]

        v = self.cli("show ip interface")
        for match in self.rx_ip.finditer(v):
            ifname = match.group("ifname")
            admin_status = bool(match.group("admin_status") == "up")
            oper_status = bool(match.group("oper_status") == "up")
            iface = {
                "name": ifname,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["IPv4"],
                        "ip_addreses": [match.group("ip")],
                        "mtu": match.group("mtu"),
                    }
                ],
            }
            c = self.cli("show interface %s" % ifname)
            match1 = self.rx_mac.search(c)
            iface["mac"] = match1.group("mac")
            iface["subinterfaces"][0]["mac"] = match1.group("mac")
            if ifname.startswith("vlan"):
                iface["type"] = "SVI"
                iface["subinterfaces"][0]["vlan_ids"] = [ifname[4:]]
            else:
                raise self.NotSupportedError()
            interfaces += [iface]

        return [{"interfaces": interfaces}]
