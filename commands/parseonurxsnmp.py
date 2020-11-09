#!/usr/bin/python3
import requests
from requests.auth import HTTPDigestAuth
import json
import re
import os
from pprint import pprint
import argparse
from pprint import pprint

from noc.core.management.base import BaseCommand

class Command(BaseCommand):
 def add_arguments(self, parser):
    parser.add_argument("-r", "--rx", dest="onurx", default=None)
    parser.add_argument("-u", "--onus", dest="onus", default=None)
    parser.add_argument("-o", "--olt", dest="olt", default=None)

 def loadonu(self,f):
    regex = re.compile(r"^SNMPv2-SMI::enterprises\.3902\.1012\.3\.28\.1\.1\.5\.(?P<oid>\d+\.\d+)\s+=\s+Hex-STRING:\s+(?P<sn1>\S\S\s\S\S\s\S\S\s\S\S)\s(?P<sn2>.+)$")
    result = {}
    with open(f,'r') as file:
       for line in file:
         m = regex.match(line.rstrip(os.linesep))
         sn_first = m.group(2).split()
         snstring=''
         for i in sn_first:
             snstring+=bytes.fromhex(i).decode('utf-8')
         snstring+=m.group(3).replace(' ','')
         result.update({m.group(1):snstring})
       file.close()
    return result

 def loadonusignal(self, f):
    regex = re.compile(r"^SNMPv2-SMI::enterprises\.3902\.1012\.3\.50\.12\.1\.1\.10\.(?P<oid>\d+\.\d+)\.\d+\s+=\s+INTEGER:\s+(?P<signal>.+)$")
    result = {}
    with open(f,'r') as file:
       for line in file:
         m = regex.match(line.rstrip(os.linesep))
         RxPower = int(m.group(2))
         if RxPower == 65535:
            RxPower = 0
         else:
           if RxPower > 30000:
             RxPower = (RxPower-65536)*0.002-30
           else:
             RxPower = RxPower*0.002-30
         result.update({m.group(1):RxPower})
       file.close()
    return result

 def loadolt(self,f):
    regex = re.compile(r"^SNMPv2-SMI::enterprises\.3902\.1082\.500\.20\.2\.1\.2\.1\.3\.(?P<oid>\d+\.\d+)\s+=\s+Hex-STRING:\s+(?P<sn1>\S\S\s\S\S\s\S\S\s\S\S)\s(?P<sn2>.+)$")
    result = {}
    try:
     with open(f,'r') as file:
       for line in file:
         m = regex.match(line.rstrip(os.linesep))
         sn_first = m.group(2).split()
         snstring=''
         for i in sn_first:
             snstring+=bytes.fromhex(i).decode('utf-8')
         snstring+=m.group(3).replace(' ','')
         result.update({m.group(1):snstring})
       file.close()
    except:
       result = {}
    return result

 def loadoltsignal(self, f):
    regex = re.compile(r"^SNMPv2-SMI::enterprises\.3902\.1082\.500\.1\.2\.4\.2\.1\.2\.(?P<oid>\d+\.\d+)\s+=\s+INTEGER:\s+(?P<signal>.+)$")
    result = {}
    try:
     with open(f,'r') as file:
       for line in file:
         m = regex.match(line.rstrip(os.linesep))
         RxPower = int(m.group(2))/1000
         result.update({m.group(1):RxPower})
       file.close()
    except:
       result = {}
    return result

 def handle(self, *args, **options):
    fonus = options.get("onus")
    frx = fonus.replace('onulist','onurx')
    foltrx = fonus.replace('onulist','oltrx')
    foltonu = fonus.replace('onulist','oltonulist')
    olt = options.get("olt")
    path,fname = os.path.split(fonus)
    tail = fname.split('.')
    tail.reverse()
    timestamp = tail[0]
    olt = options.get("olt")
    onu = self.loadonu(fonus)
    onurx = self.loadonusignal(frx)
    oltonu = self.loadolt(foltonu)
    oltrx = self.loadoltsignal(foltrx)
    signals=[]
    signals2=[]
    for key in onu:
        signals.append([onu[key],round(onurx[key],2),timestamp])
        print('ponsignals,olt={},sn={},who=onurx value={} {}000000000'.format(olt,onu[key],round(onurx[key],2),timestamp));
    for key in oltonu:
        signals2.append([oltonu[key],round(oltrx[key],2),timestamp])
        print('ponsignals,olt={},sn={},who=oltrx value={} {}000000000'.format(olt,oltonu[key],round(oltrx[key],2),timestamp));
#    pprint(signals2)


if __name__ == "__main__":
    Command().run()