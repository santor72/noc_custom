# coding: utf-8
import json
from noc.core.management.base import BaseCommand
from noc.custom.lib.gettopology import create_topology

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--by", dest="by", default=None)
        parser.add_argument("-v", "--values", dest="values", default=None)
    def handle(self, *args, **options):
        by = options.get("by")
        values = options.get("values").split(',')
        if not by:
            print("Need --by")
            quit()
        if not values:
            print("Need --values")
            quit()
        topojson = create_topology(by, values)
        self.stdout.write("@@@\n%s\n@@@\n" % (json.dumps(topojson)))

if __name__ == "__main__":
    Command().run()
