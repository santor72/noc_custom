# coding: utf-8
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-s", "--selector", dest="selector", default=None)

    def handle(self, *args, **options):
        connect()
        selector_name = options.get("selector")
        if selector_name:
           selector = ManagedObjectSelector.objects.filter(name=selector_name)
           s=[]
           mo=selector[0].managed_objects
           for item in mo:
            s.append(item.address)
           print('Script resutl\n')
           print(' '.join(s))
        else:
            print("Need --selector parametr")

if __name__ == "__main__":
    Command().run()
