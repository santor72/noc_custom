# coding: utf-8
import re
import pickle

from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.bi.models.mac import MAC as MACDBC
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.mac import MAC


class Command(BaseCommand):
    def handle(self, *args, **options):
        macdb = MACDBC()
        connect()
        bras=ManagedObject.objects.get(name='point-BNG01-podolsk')
        print('Get sessions')
        res_sessions_det = bras.scripts.commands(commands=["show subscriber session all detail location 0/RSP0/CPU0"])
        sessions={}
        notfound={}
        if res_sessions_det.get('output') and res_sessions_det['output']:
            sessionlist = res_sessions_det['output'][0].split('\n\n')
            rx_sh_session = re.compile(
                r"^[\S+|\s+]+Mac Address:\s+(?P<mac>\S+)\n[\S+|\s+]+\nUser Name:\s+(?P<login>\S+)\n[\S+|\s+]+\nOuter VLAN ID:\s+(?P<vlan>\S+)[\S+|\s+]+$",
                re.MULTILINE | re.IGNORECASE
            )
            for item in sessionlist:
                sessiondata = rx_sh_session.match(item)
                if sessiondata:
                    newitem = {'mac': sessiondata.group('mac'), 'vlan': sessiondata.group('vlan'),'bi_id':'','interface':''}
                    mac = int(MAC(MACAddressParameter(accept_bin=False).clean(sessiondata.group('mac'))))
                    m=macdb.mac_filter({"mac": mac})
                    for p in m:
                        if re.match(r'^gpon-olt',p["interface"]) and p["vlan"] == sessiondata.group('vlan'):
                            newitem['bi_id'] = p['managed_object']
                            newitem['interface'] = p['interface']
                    if newitem['interface']:
                        sessions[sessiondata.group('login')]=newitem
                    else:
                        notfound[sessiondata.group('login')]=newitem  
        with open('/tmp/sessions.pickle', 'wb') as f:
            pickle.dump(sessions,f)
        with open('/tmp/sessionsnotfound.pickle', 'wb') as f:
            pickle.dump(notfound,f)

if __name__ == "__main__":
    Command().run()

