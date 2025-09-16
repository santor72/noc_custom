import time
from sqlalchemy import text
from sqlalchemy.engine import create_engine
from typing import Dict, List, Any
import pandas as pd

from noc.core.mac import MAC
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc_custom.lib.script  import Command as  Command2
from noc.sa.models.managedobject import ManagedObject

mos = [
    'mskix-7600',
    'k18.gw',
    'mgs-rcod-asr1',
    'din-me3400.gw',
    'dc-pemz-7600',
    'skl-104-7600-217.76.46.129',
    'trikolor.gw',
    'v150-gw-asr1001',
    'FM_LuiVit',
    'point-HW6730-CHPK',
    'АбрауДюрсо-217.76.46.131',
    'chv-Huawei6720',
    'mskix-hw6730-sw02',
    'sidorovo-yandex-hw5720-217.76.46.244',
    'Lvov-Krasnaya18-10.76.46.230',
    'skl104-Hw6720-217.76.46.246',
    'Sever-Fedotovo-hw5720',
    'Iksha_hw5320',
    'pemz-Huawei6730',
    'mskix-hw6320-217.76.46.108',
    'Sever-Durikino-hw5720-10.76.46.220',
    'm34-hw6720',
    'sher_hw5720-10.76.46.223',
    'k18-Huawei5320-10.76.46.19',
    'Ovchinki-Hw6730-10.76.46.227',
    'talalihino10-hw5320',
    '10.76.46.226_ButovoPark',
    'plk78-Huawei6730-217.76.46.130'
]

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-p", dest="isprint", default=None)
#        parser.add_argument("object_name", nargs=1, help="Object name")
    def handle(self,  *args, **options):
#        object_name = options.get("object_name")
        connect()
        isprint = options.get("isprint")
        c = Command2()
        now = time.localtime()
        date = time.strftime("%Y-%m-%d", now)
        ts = time.strftime("%Y-%m-%d %H:%M:%S", now)
        for i in mos:
            print(i)
            #mo =  ManagedObject.objects.filter(name=object_name[0]).first()
            try:
                mo =  ManagedObject.objects.filter(name=i).first()
                r = c.handle(
                    ['get_ip_discovery'],
                    [i],
                    arguments=[],
                    pretty=False,
                    yaml_o=False,
                    use_snmp=True,
                    access_preference=None,
                    snmp_rate_limit=0,
                    update_spec=None,
                    beef_output=None
                    )
                r1 = []
                for vpn in r:
                    for a in vpn["addresses"]:
                        arp = MAC(a.get("mac"))
                        r1 += [{
                                "vpn_id": str(vpn.get("vpn_id")),
                                "rd": vpn.get("rd"),
                                "address": a["ip"],
                                "interface": a.get("interface"),
                                "managed_object": mo.bi_id,
                                "arp": int(arp),
                                "ts": ts,
                                "date": date
                        }]
                if r1:
                    engine_c = create_engine('clickhouse://noc:noc@10.8.0.105:8123/noc')
                    df = pd.DataFrame.from_dict(r1)
                    df.to_sql("raw_arp", engine_c, index=False, if_exists='append')
                if isprint:
                    print(r)
            except:
                pass

if __name__ == "__main__":
    Command().run()
