from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.archivedalarm import ArchivedAlarm
from datetime  import *

alarms = ActiveAlarm.objects()
events = ActiveEvent.objects()
ar_alarms = ArchivedAlarm.objects()

for alarm in alarms:
   if alarm.timestamp < datetime.now() - timedelta(2):
    alarm.delete()

for alarm in ar_alarms:
   if alarm.timestamp < datetime.now() - timedelta(2):
    alarm.delete()

for event in events:
   if alarm.timestamp < datetime.now() - timedelta(2):
    event.delete()

