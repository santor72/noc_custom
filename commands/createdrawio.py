import networkx as nx
import json
import re
from pprint import pprint
import uuid
import argparse
from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
from noc.core.management.base import BaseCommand
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", dest="fin", default=None)
        parser.add_argument("-o", "--output", dest="fout", default=None)

    def handle(self, *args, **options):
        connect()
        fin = options.get("fin")
        fout = options.get("fout")
        if not fin:
            print("Need --file for input file name and --out for output file name")
            quit()
        if not fout:
            print("Need --file for input file name and --out for output file name")
            quit()            
        #Read template files
        connect()
        #with open("/opt/noc_custom/templates/weathermap/panel.json", 'r') as f:
        #    panel = json.load(f)
        #with open("/opt/noc_custom/templates/weathermap/node.json", 'r') as f:
        #    nodetemplate = json.load(f)
        #with open("/opt/noc_custom/templates/weathermap/link.json", 'r') as f:
        #    linktemplate = json.load(f)
        #with open("/opt/noc_custom/templates/weathermap/target.json", 'r') as f:
        #    targettemplate = json.load(f)
        with open("/opt/noc_custom/templates/weathermap/icons.json", 'r') as f:
            icons = json.load(f)
        #Read input file and create newnodes and links dict from nocdb
        with open(fin, 'r') as f:
            monames = json.load(f)
        newnodes={}
        for moname in monames:
            MOs = ManagedObject.objects.filter(name=moname)
            if MOs:
                mo = MOs[0]
                newnodes[mo.id] = {
                    'id': str(mo.id),
                    'label':mo.name, 
                    "nodeResolution": 8,
                    'data': {
                        'bi_id':mo.bi_id,
                        'icon':mo.object_profile.shape,
                        'address': mo.address,
                        'description': mo.description,
                        'remote_system': mo.remote_system.name,
                        'remote_id': mo.remote_id
                        }
                    }
        alllinks = Link.objects.filter(linked_objects__in=[x for x in newnodes.keys()])
        links_tmp=[]
        newlinks=[]
        for k in newnodes.keys():
            l = (alllinks.filter(linked_objects__in=[k])).filter(linked_objects__in=[x for x in newnodes.keys() if x != k])
            for item in l:
                if not item.id in links_tmp:
                    links_tmp.append(item.id)
                    newlinks.append(item)
        #Create json
        result = {
            "links":[],
            "nodes": []
            }
        for k in newnodes.keys():
            result['nodes'].append(newnodes[k])
        pm_template_path='/opt/noc_custom/templates/draw.io'
        j2_env = Environment(loader=FileSystemLoader(pm_template_path))
        target_template = j2_env.get_template('query.j2')
        for v in newlinks:
            linka=v.interfaces[0].managed_object.id
            linkb=v.interfaces[1].managed_object.id
            #Interface names in link
            inta=v.interfaces[0].name
            intb=v.interfaces[1].name
            la = re.sub('\W+','_', newnodes[linka]['label']+'_'+newnodes[linkb]['label'])
            lb = re.sub('\W+','_', newnodes[linkb]['label']+'_'+newnodes[linka]['label'])
            target_a = target_template.render(
                name=la,
                bi_id= newnodes[linka]['data']['bi_id'],
                interface= v.interfaces[0].name
            )
            target_b = target_template.render(
                name=lb,
                bi_id= newnodes[linkb]['data']['bi_id'],
                interface= v.interfaces[1].name
                )
            result['links'].append(
                {
                    "label": "",
                    "source": str(v.interfaces[0].managed_object.id),
                    "src_label": "",
                    "target": str(v.interfaces[1].managed_object.id),
                    "trgt_label": "",
                    "data": {
                        "target_a": target_a,
                        "target_b": target_b
                    }
                }
            )
        with open(fout,'w') as f:
            #json.dump(template.render(graf=graf,nodes=nodes), f)
            f.write(json.dumps(result))
        pprint(result)

if __name__ == "__main__":
    Command().run()