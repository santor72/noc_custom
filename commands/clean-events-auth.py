from datetime  import *
import re
from noc.fm.models.activeevent import ActiveEvent
from noc.core.mongo.connection import connect
from noc.fm.models.eventclass import EventClass

connect()
class_names = [ 'Security | Authentication | Login',
                'Security | Authentication | Logout',
                'Security | Audit | Command'
              ]
re_events=re.compile(".+[LOGIN|LOGOUT|login|logout].+217.76.35.203")
re2_events=re.compile(".+217.76.35.203.+")

for eclass in EventClass.objects.filter(name__in=class_names):
 events = ActiveEvent.objects.filter(event_class=eclass)
 for event in events:
  if 'message' in event.raw_vars:
    if re_events.match(event.raw_vars['message']):
       print(event.id)
       event.delete()
  if '1.3.6.1.2.1.16.9.1.1.2.178' in event.raw_vars:
    if re2_events.match(event.raw_vars['1.3.6.1.2.1.16.9.1.1.2.178']):
       print(event.id)
       event.delete()

