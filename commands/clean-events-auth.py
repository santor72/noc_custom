from noc.fm.models.activeevent import ActiveEvent
from datetime  import *
import re

events = ActiveEvent.objects()

re_events=re.compile(".+[LOGIN|LOGOUT|login|logout].+217.76.35.203")
events = ActiveEvent.objects()
for event in events:
  if 'message' in event.raw_vars:
    if re_events.match(event.raw_vars['message']):
       event.delete()

re2_events=re.compile(".+217.76.35.203.+")
for event in events:
  if '1.3.6.1.2.1.16.9.1.1.2.178' in event.raw_vars:
    if re2_events.match(event.raw_vars['1.3.6.1.2.1.16.9.1.1.2.178']):
       event.delete()

