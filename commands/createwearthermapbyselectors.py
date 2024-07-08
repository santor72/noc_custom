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
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.networksegment import NetworkSegment

class Command(BaseCommand):
    def help(self):
        print("""Need selector
        \t-a --admindomain for admindomain(admindomains or comma separated admindomains )
        \t-s --segment for segment(or comma separated segments )
        \t-l --labels for label(or comma separated labels )
        \t-d, --dashboard if you want write dashboard file
        \t-t --title dashboard title
        \t-i for make interface panel
        \t-w for make weathermap panel
        \t--dia for write diagram file

        File write to /home/netmaps
        \t /dashboard - dashboards json. Add subdir to file name
        \t /diagram - dia files
        """)
    def add_arguments(self, parser):
        parser.add_argument("-a", "--admindomain", dest="admindomain", default=None)
        parser.add_argument("-l", "--labels", dest="labels", default=None)
        parser.add_argument("-s", "--segment", dest="segment", default=None)
        parser.add_argument("-i", "--interface", dest="intgraph", action='store_true')
        parser.add_argument("-d", "--dashboard", dest="dashout", default=None)
        parser.add_argument("-w", "--weather", dest="weather", action='store_true')
        parser.add_argument("--dia", dest="dia", default=None)
        parser.add_argument("-t", "--title", dest="title", default=None)
   
    def makenodes(self,newnodes,graf):
        nodes=[]
        xstart=100
        ystart=100
        with open("/opt/noc_custom/templates/weathermap/icons.json", 'r') as f:
            icons = json.load(f)
        for k,v in newnodes.items():
            uid=str(uuid.uuid1())
            newnodes[k]['uuid'] = uid
            if icons.get(v['icon']):
                icon = icons.get(v['icon'])
            else:
                icons.get('default')
            node = {
                'id': uid,
                'noc_id': k,
                'bi_id': v.get('bi_id'),
                'label': v.get('name'),
                'iconname': icon['name'],
                'iconpath': icon['src'],
#                'x': xstart,
#                'y': ystart
                'x': int(graf[k][0])+400,
                'y': int(graf[k][1])+400
                }
            nodes.append(node)
            xstart+=35
            ystart+=35
        return nodes
  
    def makelinks(self,nodes,newlinks):
        interfacegraph=[]
        links=[]
        targets=[]
        for v in newlinks:
            #MO id in link
            linka=v.interfaces[0].managed_object.id
            linkb=v.interfaces[1].managed_object.id
            nodea=([x for x in nodes if x['noc_id'] == linka])[0]
            nodeb=([x for x in nodes if x['noc_id'] == linkb])[0]
            #Interface names in link
            inta=v.interfaces[0].name
            intb=v.interfaces[1].name
            la = re.sub('\W+','_', nodea['label']+'_'+nodeb['label'])
            lb = re.sub('\W+','_', nodeb['label']+'_'+nodea['label'])            
            links.append(
                {
                    'id' : str(uuid.uuid1()),
                    'nodea' : nodea,
                    'nodeb' : nodeb,
                    'query_a' : la,
                    'query_b' : lb,
                    'bandwidth' : v.interfaces[0].in_speed*1000 if v.interfaces[0].in_speed else 0
                }
            )
            targets.append({
                'name':la,
                'bi_id': nodea['bi_id'],
                'interface': v.interfaces[0].name
            })
            targets.append({
                'name':lb,
                'bi_id': nodeb['bi_id'],
                'interface': v.interfaces[1].name
            })
            #Графики для интерфейсов
            gname=re.sub('\W+','_',f"{v.interfaces[0].managed_object.name} {v.interfaces[0].description}({v.interfaces[0].name})")
            interfacegraph.append(
                f"{gname} : {v.interfaces[0].managed_object.bi_id};{v.interfaces[0].name}"
            )
            gname=re.sub('\W+','_',f"{v.interfaces[1].managed_object.name} {v.interfaces[1].description}({v.interfaces[1].name})")
            interfacegraph.append(
                f"{gname} : {v.interfaces[1].managed_object.bi_id};{v.interfaces[1].name}"
            )
        return [links, targets, interfacegraph]
    
    def handle(self, *args, **options):
        connect()
        #Читаем входные параметры
        padmindomain = options.get("fin")
        plabels = options.get("labels")
        psegment = options.get("segment")
        intgraph = options.get("intgraph")
        weather = options.get("weather")
        dashout = options.get("dashout")
        dia = options.get("dia")
        title = options.get("title")
        #Обрабатываем параметры
        admindomains = padmindomain.split(',') if padmindomain else [] 
        labels = plabels.split(',') if plabels else []
        segments = psegment.split(',') if psegment else []
        if not (admindomains or labels or segments or title):
            self.help()
            quit()
        connect()
        #Read template files
        pm_template_path='/opt/noc_custom/templates/weathermap'
        j2_env = Environment(loader=FileSystemLoader(pm_template_path))
        template = j2_env.get_template('dahsboard.j2')
        moids=[]
        if admindomains:
            admdom = AdministrativeDomain.objects.filter(name__in=admindomains)
            mo_by_admdomain = ManagedObject.objects.filter(administrative_domain__in=admdom)
            for item0 in mo_by_admdomain:
                moids.append(item0)
        if segments:
            seg = NetworkSegment.objects.filter(name__in=segments)
            mo_by_segment = ManagedObject.objects.filter(segment__in=seg)
            for item1 in mo_by_segment:
                if not item1 in moids:
                    moids.append(item1)
        if labels:
            mo_by_label = ManagedObject.objects.filter(labels__contains=labels)
            for item2 in mo_by_label:
                if not item2 in moids:
                    moids.append(item2)
        newnodes={}
        for mo in moids:
            newnodes[mo.id] = {'name':mo.name, 'id': mo.id,'bi_id':mo.bi_id,'icon':mo.object_profile.shape}
        alllinks = Link.objects.filter(linked_objects__in=[x for x in newnodes.keys()])
        links_tmp=[]
        newlinks=[]
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
        #Make node list for template
        nodes = self.makenodes(newnodes,Gl)
        #Make link list for template
        links,targets,interfacegraph = self.makelinks(nodes,newlinks)
        graf={'uuid': str(uuid.uuid1())}
        #write dashboard
        result = None
        if intgraph and weather:
            result = template.render(title=title,graf=graf,nodes=nodes,links=links,targets=targets, intgraph=1, i3=",".join(interfacegraph))
        elif weather:
            result = template.render(title=title,graf=graf,nodes=nodes,links=links,targets=targets, intgraph=0, i3="")
        elif intgraph:
            result = template.render(title=title,graf=graf,nodes=[],links=[],targets=[], intgraph=1, i3=",".join(interfacegraph))
        if dashout and result:
            with open("/home/netmaps/grafana/dashboards/"+dashout,'w') as f:
            #json.dump(template.render(graf=graf,nodes=nodes), f)
                f.write(result)

if __name__ == "__main__":
    Command().run()