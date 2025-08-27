from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedalarm import ArchivedAlarm
from datetime  import *
from noc.core.mongo.connection import connect
connect()

alarms = ActiveAlarm.objects()
events = ActiveEvent.objects()
ar_alarms = ArchivedAlarm.objects()
delta=15
for alarm in alarms:
 if alarm.timestamp:
   if alarm.timestamp < datetime.now() - timedelta(days=delta):
    alarm.delete()
 else:
   alarm.delete()

for alarm in ar_alarms:
 if alarm.timestamp:
   if alarm.timestamp < datetime.now() - timedelta(days=delta):
    alarm.delete()
 else:
   alarm.delete()

for  event in events:
 if event.timestamp:
   if event.timestamp < datetime.now() - timedelta(days=delta):
    event.delete()
 else:
   event.delete()
