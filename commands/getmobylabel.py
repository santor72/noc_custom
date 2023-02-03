# coding: utf-8
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-s", "--selector", dest="selector", default=None)
        parser.add_argument("-p", "--profile", dest="profile", default=None)

    def handle(self, *args, **options):
        connect()
        selector_name = options.get("selector")
        profile_name = options.get("profile")
        if selector_name:
           if profile_name:
              p=Profile.objects.filter(name=profile_name)
              if p:
                 mo=  ManagedObject.objects.filter(labels__contains=[selector_name],profile=p[0])
              else:
                 print('Profile name error\n')
                 return 0
           else:
              mo=  ManagedObject.objects.filter(labels__contains=[selector_name])
           s=[]
           for item in mo:
            s.append(item.address)
           print('Script resutl\n')
           print(' '.join(s))
        else:
            print("Need --selector parametr")

if __name__ == "__main__":
    Command().run()
