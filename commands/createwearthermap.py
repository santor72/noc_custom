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
        parser.add_argument("-i", "--interface", dest="intgraph", default=None)
    def handle(self, *args, **options):
        connect()
        fin = options.get("fin")
        fout = options.get("fout")
        intgraph = options.get("intgraph")
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
                newnodes[mo.id] = {'name':mo.name, 'id': mo.id,'bi_id':mo.bi_id,'icon':mo.object_profile.shape}
        alllinks = Link.objects.filter(linked_objects__in=[x for x in newnodes.keys()])
        links_tmp=[]
        newlinks=[]
        interfacegraph=[]
        for k in newnodes.keys():
            l = (alllinks.filter(linked_objects__in=[k])).filter(linked_objects__in=[x for x in newnodes.keys() if x != k])
            for item in l:
                if not item.id in links_tmp:
                    links_tmp.append(item.id)
                    newlinks.append(item)
        #Create graf template
        G = nx.Graph()
        for k,v in newnodes.items():
            G.add_node(k)
        for v in newlinks:
            G.add_edge(v.interfaces[0].managed_object.id, v.interfaces[1].managed_object.id)
        Gl=nx.nx_agraph.graphviz_layout(G)
        #newlinks=[]
        #for k,v in links.items():
        #    newlinks.append({x.managed_object.id:x.name for x in v.interfaces})
        #Make node list for template
        nodes=[]
        nodesbyid={}
        xstart=100
        ystart=100
        for k,v in newnodes.items():
            uid=str(uuid.uuid1())
            newnodes[k]['uuid'] = uid
            if icons.get(v['icon']):
                icon = icons.get(v['icon'])
            else:
                icons.get('default')
            node = {
                'id': uid,
                'bi_id': v.get('bi_id'),
                'label': v.get('name'),
                'iconname': icon['name'],
                'iconpath': icon['src'],
#                'x': xstart,
#                'y': ystart
                'x': int(Gl[k][0])+400,
                'y': int(Gl[k][1])+400
                }
            nodes.append(node)
            nodesbyid[k] = node
            xstart+=35
            ystart+=35
        #Make link list for template
        links=[]
        targets=[]
        for v in newlinks:
            #MO id in link
            linka=v.interfaces[0].managed_object.id
            linkb=v.interfaces[1].managed_object.id
            #Interface names in link
            inta=v.interfaces[0].name
            intb=v.interfaces[1].name
            la = re.sub('\W+','_', newnodes[linka]['name']+'_'+newnodes[linkb]['name'])
            lb = re.sub('\W+','_', newnodes[linkb]['name']+'_'+newnodes[linka]['name'])            
            links.append(
                {
                    'id' : str(uuid.uuid1()),
                    'nodea' : nodesbyid[linka],
                    'nodeb' : nodesbyid[linkb],
                    'query_a' : la,
                    'query_b' : lb,
                    'bandwidth' : v.interfaces[0].in_speed*1000
                }
            )
            targets.append({
                'name':la,
                'bi_id': nodesbyid[linka]['bi_id'],
                'interface': v.interfaces[0].name
            })
            targets.append({
                'name':lb,
                'bi_id': nodesbyid[linkb]['bi_id'],
                'interface': v.interfaces[1].name
            })
            #Графики для интерфейсов
            gname=re.sub('\W+','_',f"{v.interfaces[0].managed_object.name} {v.interfaces[0].description}({v.interfaces[0].name})")
            interfacegraph.append(
                f"{gname} : {v.interfaces[0].managed_object.bi_id};{v.interfaces[0].name}"
            )
#            gname=re.sub('\W+','_',f"{v.interfaces[1].managed_object.name} {v.interfaces[1].description}({v.interfaces[1].name})")
#            interfacegraph.append(
#                f"{gname} : {v.interfaces[1].managed_object.bi_id};{v.interfaces[1].name}"
#            )
        graf={'uuid': str(uuid.uuid1())}
        pm_template_path='/opt/noc_custom/templates/weathermap'
        j2_env = Environment(loader=FileSystemLoader(pm_template_path))
        template = j2_env.get_template('dahsboard.j2')
        if intgraph:
            result = template.render(graf=graf,nodes=nodes,links=links,targets=targets, intgraph=1, i3=",".join(interfacegraph))
        else:
            result = template.render(graf=graf,nodes=nodes,links=links,targets=targets, intgraph=0, i3="")
        with open(fout,'w') as f:
            #json.dump(template.render(graf=graf,nodes=nodes), f)
            f.write(result)
        print(result)
        #print(Gl)

if __name__ == "__main__":
    Command().run()