from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedalarm import ArchivedAlarm
from datetime  import *
from noc.core.mongo.connection import connect
from noc.fm.models.eventclass import EventClass
connect()
class_names = [ 'Unknown | Syslog',
      'Unknown | SNMP Trap'
    ]

for eclass in EventClass.objects.filter(name__in=class_names):
 events = ActiveEvent.objects.filter(event_class=eclass)
 for e in events:
    print(e.id)
    e.delete()
