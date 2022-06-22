# coding: utf-8
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from datetime import datetime, timedelta
from dateutil import tz
from noc.core.clickhouse.connect import ClickhouseClient
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.core.mac import MAC

class Command(BaseCommand):
    def add_arguments(self, parser):
        today = datetime.utcnow().date()
        start = datetime(today.year, today.month, today.day, tzinfo=tz.tzutc())
        end = start + timedelta(1)
        parser.add_argument("-m", "--mac", dest="mac", default=None)
        parser.add_argument("-s", "--start", dest="ts_start", default=start)
        parser.add_argument("-e", "--end", dest="ts_end", default=end)
        parser.add_argument("-o", "--mo", dest="mo", default=None)

    def handle(self, *args, **options):
        mac = options.get("mac")
        moname = options.get("mo")
        mo = None
        start = options.get("ts_start")
        if not isinstance(start, str):
            start=int(start.timestamp())
        end = options.get("ts_end")
        if not isinstance(end, str):
            end = int(end.timestamp())
        if mac:
           connect()
           if moname:
              mo = ManagedObject.objects.filter(name=moname)
              if not mo:
                 print('Can`t find MO')
                 return -1
           print(start)
           print(end)
           ch = ClickhouseClient()
           mac = MAC(mac)

           query = f"select * from mac where mac={int(mac)} and  ts > {start} and ts <  {end}"
           if mo:
              query = f"{query} and managed_object = {mo[0].bi_id}"
           query = f"{query} order by ts"
           data = ch.execute(query)

           for item in data:
               if not mo:
                  mo = ManagedObject.objects.filter(bi_id=item[2])
               i = Interface.objects.filter(name = item[4], managed_object=mo[0].id)
               if i[0].is_linked:
                  print(f"{item[1]} - {mo[0].name} - {item[4]} - {i[0].link.__str__()}")
               else:
                  print(f"{item[1]} - {mo[0].name} - {item[4]}")

        else:
            print("Need --account parametr")

if __name__ == "__main__":
    Command().run()

