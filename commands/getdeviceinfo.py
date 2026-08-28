# coding: utf-8
from typing import List, Dict, Any, Optional
from pprint import pprint
import argparse
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface

class Command(BaseCommand):
    def get_device_info(self, mo: ManagedObject) -> Dict:
        return {
            "name": mo.name,
            "vendor": mo.vendor.name,
            "network_role": mo.object_profile.name,
            "platform": mo.platform.full_name,
            "version": mo.version.full_name
        }
    def get_device_iface(self, mo: ManagedObject) -> List:
        ifaces = Interface.objects.filter(managed_object = mo.id)
        return [x.name for x in ifaces if x.type=='physical']

    def get_keywords(self) -> Dict:
        keywords = {'general': self.get_device_info, "ifaces": self.get_device_iface}
        return keywords

    def get_run(self, key: str, ip: str) -> Any:
        mo = ManagedObject.objects.filter(address=ip).first()
        if mo:
            keywords = self.get_keywords()
            if not key in keywords.keys():
               return "No keyword found"
            return keywords[key](mo)
        else:
            return "No device found by IP address"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--ip", dest="ip", default="i")
        parser.add_argument("-k", "--keyword", dest="keyword", default="k")

    def handle(self, *args, **options):
        ip = options.get("ip")
        keyword = options.get("keyword")
        connect()
        print("@@@\n")
        if ip and keyword:
            pprint(self.get_run(keyword,ip))
        else:
            print("Need --ip and --keyword  parametr")
        print("\n@@@\n")

if __name__ == "__main__":
    Command().run()
