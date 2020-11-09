# coding: utf-8
import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import argparse

#NOC modules
from noc.core.management.base import BaseCommand
from noc.main.models.remotesystem import RemoteSystem, EnvItem
from noc.core.mongo.connection import connect

url = "https://api.ccs.ru/php7/api/v1/utm5/"
headers = {'Content-type': 'application/json'}

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--login", dest="login", default=None)

    def handle(self, *args, **options):
	login = options.get("login")
	connect()
	r = url + 'user/' + login + '/session'
	response = requests.get(r,verify=True,  headers=headers)
	if (response.ok):
		usession =  json.loads(response.content)
      	else:
        	response.raise_for_status()
        if (usession['Result'] == 'Ok'):
    	    print(usession['data'])
    	else:
    	    print(usession)

if __name__ == "__main__":
    Command().run()    
