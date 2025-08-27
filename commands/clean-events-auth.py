from datetime  import *
import re
from noc.fm.models.activeevent import ActiveEvent
from noc.core.mongo.connection import connect
from noc.fm.models.eventclass import EventClass
from tqdm import tqdm

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", default=0)
args = parser.parse_args()
debug = args.debug

connect()
from datetime  import *
import re
from noc.fm.models.activeevent import ActiveEvent
from noc.core.mongo.connection import connect
from noc.fm.models.eventclass import EventClass
from tqdm import tqdm

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", default=0)
args = parser.parse_args()
debug = args.debug

connect()
class_names = [ r"^Security.+[L|l]ogin$",
                r"^Security.+[L|l]ogout",
                r"Security.+[c|C]ommand$",
                r"^Security.+SNMP\s+Authentication\s+Failure$",
                r"Security\s+Authentication\s+Security.+[c|C]ommand$",
                r"^Security.+SNMP\s+Authentication\s+Failure$",
                r"Security\s+Authentication\s+Failed$"
              ]

re_events=re.compile(".+[LOGIN|LOGOUT|login|logout].+217.76.35.203")
re2_events=re.compile(".+217.76.35.203.+")

for cname in class_names:
 if debug:
    print(cname)
 re_pattern = re.compile(cname)
 eclass = EventClass.objects.filter(name__regex=re_pattern).first()
 if not eclass:
   continue
 print(eclass)
 events = ActiveEvent.objects.filter(event_class=eclass)
 print(len(events))
 continue
 if debug == 1:
   i = tqdm(events)
 else:
   i = events
 for event in i:
  if 'message' in event.raw_vars:
    if re_events.match(event.raw_vars['message']):
       print(event.id)
       event.delete()
  if '1.3.6.1.2.1.16.9.1.1.2.178' in event.raw_vars:
    if re2_events.match(event.raw_vars['1.3.6.1.2.1.16.9.1.1.2.178']):
       print(event.id)
       event.delete()

