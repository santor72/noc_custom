# coding: utf-8
from pprint import pprint

from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject

l = {
    '217.76.46.131' :'10.77.46.131',
    '10.76.46.230' :'10.77.46.230',
    '217.76.46.246' :'10.77.46.246',
    '10.76.46.221' :'10.77.46.221',
    '10.76.46.224' :'10.77.46.224',
    '10.76.46.220' :'10.77.46.220',
    '217.76.46.116' :'10.77.46.116',
    '10.76.46.19' :'10.77.46.19',
    '217.76.46.108' :'10.77.46.108',
    '217.76.46.20' :'10.77.46.20',
    '217.76.46.244' :'10.77.46.244',
    '10.76.46.223' :'10.77.46.223',
    '10.76.46.227' :'10.77.46.227',
    '10.76.46.168' :'10.77.46.168',
    '10.76.46.226' :'10.77.46.226',
    '217.76.46.130' :'10.77.46.130'
}
l2 = {
    '217.76.46.119' :'10.77.46.119',
    '10.76.46.18' :'10.77.46.18',
    '10.76.46.208' :'10.77.46.208',
    '217.76.33.166' :'10.77.33.166',
    '217.76.46.129' :'10.77.46.129',
    '10.76.46.205' :'10.77.46.205',
    '10.76.46.209' :'10.77.46.209',
    '10.76.46.201' :'10.77.46.201'
}
class Command(BaseCommand):
    def handle(self, *args, **options):
        connect()
        for k,v in l2.items():
           mo = ManagedObject.objects.get(address=k)
           if mo:
            commands = [
                "conf t",
                "interface LoopBack211",
                "ipv6 enable",
                "vrf forwarding service",
                f"ip address {v} 255.255.255.255",
                "end",
                "write",
                ""
            ]
            print(f"Set Loopback 211 on {k} to {v}")
            res = mo.scripts.commands(commands=commands)
            pprint(res)

    def handle2(self, *args, **options):
        connect()
        for k,v in l.items():
           mo = ManagedObject.objects.get(address=k)
           if mo:
            commands = [
                "system-view",
                "interface LoopBack211",
                "ipv6 enable",
                "ip binding vpn-instance service",
                f"ip address {v} 255.255.255.255",
                "quit",
                "quit",
                "save all",
                ""
            ]
            print(f"Set Loopback 211 on {k} to {v}")
            res = mo.scripts.commands(commands=commands)
            pprint(res)

if __name__ == "__main__":
    Command().run()
