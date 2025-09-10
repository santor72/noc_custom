# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "Cisco.IOS.get_config"
    interface = IGetConfig

    def execute_cli(self):
        config = self.cli("uci show")
        #config = self.strip_first_lines(config, 3)
        return self.cleaned_config(config)
