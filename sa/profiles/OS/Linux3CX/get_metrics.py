i# ---------------------------------------------------------------------
# 3CX.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re


# NOC modules
from noc.core.text import parse_kv
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics

class Script(GetMetricsScript):
    def execute(self, metrics):
        self.logger.debug('Yesssssssssssssssssssss')

    @metrics([
                  'Telephony | SIP | Sessions | Active'
            ],
        access="S",
        volatile=False,
    )
    def collect_telephony_metrics(self, metrics):
        self.logger.debug('Yesssssssssssssssssssss')
        

