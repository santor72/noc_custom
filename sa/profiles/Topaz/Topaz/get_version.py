# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Topaz.Topaz.get_version"
    cache = True
    interface = IGetVersion
    always_prefer = "C"
    rx_ver = re.compile(
        r"^System\s+-\s+(?P<system>\S+)\s+.*\n"
        r"^Web\s+-\s+(?P<web>\S+)\n"
        r"^kernel\s+-\s+(?P<kernel>\S+)\n"
        ,
        re.MULTILINE | re.IGNORECASE
    )
    rx_model = re.compile(
        r'.+OF: fdt: Machine model:\s+(?P<model>.+)\n',
        re.MULTILINE | re.IGNORECASE
    )

    def execute_cli(self):
        v = self.cli("version", cached=True)
        match = self.rx_ver.search(v)
        if match:
            r = {
                "vendor": "Topaz",
                "version": match.group("system"),
                "attributes": {"web": match.group("web"),"kernel": match.group("kernel")},
            }
        else:
            r = {
                "vendor": "Topaz",
                "version": "unk",
            }
        if self.has_snmp():
            try:
                s = self.snmp.get(['1.3.6.1.2.1.1.1.0'])
                hostname = (s['1.3.6.1.2.1.1.1.0'].split(' '))[1]
                r['attributes']['hostname'] = hostname
            except:
                pass
        v = self.cli("dmesg", cached=True)
        match = self.rx_model.search(v)
        if match:
            r["platform"]="Topaz-%s" % match.group("model")
        else:
            r["platform"]="Topaz"
        return r
