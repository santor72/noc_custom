# coding: utf-8
#Находит объекты маршрутизации для ip в отчете от DPIU "Top subscribers"
import csv
import re
import pickle
from ipaddress import IPv4Address, IPv4Network
from pprint import pprint
#noc modules
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect
from noc.core.management.base import BaseCommand

def findroute(s_ip):
    global mskixroutes
    for x in mskixroutes:
        if IPv4Address(s_ip) in IPv4Network(x[0]):
            return [x[0],x[1]]
    return [None,None]

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="fname", default=None)

    def handle(self, *args, **options):
        fname = options.get("fname")
        if fname:
            connect()
            with open("/home/work/data/subscribers.pickle","rb") as f:
                subscribers = pickle.load(f)

            ipdata=[]
            commands = []
            with open(fname) as f:
                reader = csv.DictReader(f,delimiter = ",")
                for row in reader:
                    ipdata.append(row) 
            for i in ipdata:
                if i.get('Subscriber'):
                    if i.get('Subscriber') in subscribers:
                        continue
                    else:
                        if re.match(r"^217.76", i['Subscriber']) or re.match(r"^185.81.6", i['Subscriber']):
                            commands.append(str(f"sh ip route {i['Subscriber']}"))
            if commands:
                mo = ManagedObject.objects.filter(address='217.76.46.119').first()
                res_routes=mo.scripts.commands(commands=commands)
                re_routes=re.compile(r'^Routing entry for\s+(?P<route>\d+.\d+.\d+.\d+/\d+)\n\s+Known via\s+\"ospf 16143\"[\s|\S]+Routing Descriptor Blocks:\n.+from\s+(?P<router>\d+.\d+.\d+.\d+)', re.MULTILINE | re.IGNORECASE)
                for row in res_routes['output']:
                    m=re_routes.match(row)
                    if m:
                        mskixroutes.append([m.group(1),m.group(2)])
            for i in ipdata:
                if i.get('Subscriber'):
                    if i.get('Subscriber') in subscribers:
                        continue
                    else:
                        if re.match(r"^217.76", i['Subscriber']) or re.match(r"^185.81.6", i['Subscriber']):
                            i['network'],i['router']  = findroute(i.get('Subscriber'))
                            subscribers[i['Subscriber']] = {'Subscriber':i['Subscriber'], 'network':i['network'], 'router': i['router']}    
                            pprint(subscribers[i['Subscriber']])     
            with open("/home/work/data/subscribers.pickle","wb") as f:
                pickle.dump(subscribers,f)   
        else:
            print("Need --file parametr")

if __name__ == "__main__":
    with open('/home/work/data/mskixroutes.pickle','rb') as f:
        mskixroutes = pickle.load(f)
    Command().run()
    with open('/home/work/data/mskixroutes.pickle','wb') as f:
        pickle.dump(mskixroutes,f)
