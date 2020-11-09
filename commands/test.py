# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
import re
from pprint import pprint
import argparse
from utm5 import UTM5
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect

class Command(BaseCommand):

    def handle(self, *args, **options):
        connect()
        from noc.sa.models.managedobject import ManagedObject
        olt = ManagedObject.objects.get(id=370)
        print(ManagedObjectAttribute.objects.get(managed_object=olt))

if __name__ == "__main__":
    Command().run()

