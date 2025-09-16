import asyncio
from noc.core.mongo.connection import connect
from gufo.ping import Ping
from time import sleep 

async def recheck(alarm):
    """
    Re-chek ping alarm and clear it if all ok
    """
    connect()
    ping=Ping()
    for x in range(4):
        sleep(10)
        result = await ping.ping(alarm.managed_object.address)
        if result:
            alarm.clear_alarm()
            break
    