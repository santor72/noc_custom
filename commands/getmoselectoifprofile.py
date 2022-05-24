# coding: utf-8
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-s", "--selector", dest="selector", default=None)
        parser.add_argument("-p", "--profile", dest="ifprofile", default=None)

    def handle(self, *args, **options):
        connect()
        selector_name = options.get("selector")
        ifprofile_name = options.get("ifprofile")
        if selector_name and ifprofile_name:
           selector = ManagedObjectSelector.objects.filter(name=selector_name)
           result=[]
           mo=selector[0].managed_objects
           for item in mo:
            for iface in Interface.objects.filter(managed_object=item.id):
               if iface.profile.name == ifprofile_name:
                  s = "{0}-{2} : {1};{2}".format(item.name, item.bi_id, iface.name)
                  result.append(s)
           print('Script resutl\n')
           print(','.join(result))
        else:
            print("Need --selector --profile parametrs")

if __name__ == "__main__":
    Command().run()
