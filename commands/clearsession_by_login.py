# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import argparse
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--login", dest="login", default=None)

    def handle(self, *args, **options):
        connect()
        login = options.get("login")
        if login:
                    #Для всех логинов, для всех брасов формируем список комманд и выполняем их
                    from noc.sa.models.action import Action
                    from noc.sa.models.managedobject import ManagedObject
                    action = Action.objects.get(name='clearsession')
                    #https://api.ccs.ru/php7/api/v1/utm5/user/15528987/session
#                    bras = [ManagedObject.objects.get(id=105), ManagedObject.objects.get(id=86), ManagedObject.objects.get(id=360)]
                    bras = [ManagedObject.objects.get(id=105), ManagedObject.objects.get(id=360)]
                    for i in range(len(bras)):
                        print("clear session on {0}".format([bras[i]]))
                        commands = str(action.expand(bras[i],username=login))
                        print("clear session on {0}".format([bras[i]]))
                        print(commands)
                        bras[i].scripts.commands(commands=commands)
        else:
            print("Need --account parametr")

if __name__ == "__main__":
    Command().run()
