"""
Recheck all ping error alarms
"""
from noc.core.mongo.connection import connect
from noc.fm.models.activealarm import ActiveAlarm
from noc.fm.models.alarmclass import AlarmClass
from gufo.ping import Ping
import asyncio

async def doping(y):
    y['result'] = await ping.ping(y["a"].managed_object.address)
async def main(ad):
    tasks = []
    for a in ad:
        tasks.append(asyncio.create_task(doping(ad[a])))
    for task in tasks:
        await task

connect()
ping=Ping()
acping=AlarmClass.objects.get(name="NOC | Managed Object | Ping Failed")
alarms = ActiveAlarm.objects.filter(alarm_class=acping)
ads = {x.managed_object.address:{"a":x} for x in alarms}
await main(ads)
for x in ads.values():
    if x['result']:
        x['a'].clear_alarm(message="Auto clear")
