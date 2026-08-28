# coding: utf-8
import json
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.resourcegroup import ResourceGroup
from noc.main.models.label import Label

def create_topology(by: str, values: list) -> dict:
        if not by:
            print("Need --by")
            return {}
        if not values:
            print("Need --values")
            return {}
        connect()
        with open("/opt/noc_custom/templates/topo-icons.json", "r") as f:
            styledict = json.load(f)
        mo_objects=[]
        if by=="admindomains":
            admdom = AdministrativeDomain.objects.filter(name__in=values)
            mo_by_admdomain = ManagedObject.objects.filter(administrative_domain__in=admdom)
            for item0 in mo_by_admdomain:
                mo_objects.append(item0)
        if by=="segments":
            seg = NetworkSegment.objects.filter(name__in=values)
            mo_by_segment = ManagedObject.objects.filter(segment__in=seg)
            for item1 in mo_by_segment:
                if not item1 in mo_objects:
                    mo_objects.append(item1)
        if by=="labels":
            mo_by_label = ManagedObject.objects.filter(labels__contains=values)
            for item2 in mo_by_label:
                if not item2 in mo_objects:
                    mo_objects.append(item2)
        if by=="names":
            for x in values:
                mo_by_name = ManagedObject.objects.filter(name=x).first()
                if mo_by_name:
                    if not mo_by_name in mo_objects:
                        mo_objects.append(mo_by_name)
        if by=="ip":
            for x in values:
                mo_by_name = ManagedObject.objects.filter(address=x).first()
                if mo_by_name:
                    if not mo_by_name in mo_objects:
                        mo_objects.append(mo_by_name)
        topojson={'nodes':[], 'links':[]}
        newnodes={}
        links_tmp=[]
        newlinks=[]
        for mo in mo_objects:
            styleid = styledict['profiles'][str(mo.object_profile_id)] if str(mo.object_profile_id) in styledict['profiles'] else "simple"
            style = styledict["styles"][styleid]
            size = styledict["sizes"][styleid]
            topojson['nodes'].append({'id': str(mo.id), 'label':mo.name,"nodeResolution": "8", "ip": mo.address, "vendor": mo.vendor.name, 
                "network_role": mo.object_profile.name,
                "platform": mo.platform.full_name,
                "version": mo.version.full_name,
                "width": size['width'], "height": size['height'],
                'style':style,
                 "data":{}
             })
            newnodes[mo.id] = {'id': mo.id, 'label':mo.name,"nodeResolution": 8, 'style':style, "data":[]}
        alllinks = Link.objects.filter(linked_objects__in=[x for x in newnodes.keys()])
        for k in newnodes.keys():
            l = (alllinks.filter(linked_objects__in=[k])).filter(linked_objects__in=[x for x in newnodes.keys() if x != k])
            for item in l:
                if not item.id in links_tmp:
                    links_tmp.append(item.id)
                    newlinks.append(item)
        for v in newlinks:
            linka=v.interfaces[0].managed_object.id
            linkb=v.interfaces[1].managed_object.id
            topojson['links'].append(
                {
                    #'id': v.id.__str__(),
                    'label': '', #f"{v.interfaces[0].managed_object.name} {v.interfaces[0].name} - {v.interfaces[1].managed_object.name} {v.interfaces[1].name}",
                    "src_label": v.interfaces[0].name,
                    'source': str(v.interfaces[0].managed_object.id),
                    "target": str(v.interfaces[1].managed_object.id),
                    "trgt_label": v.interfaces[1].name,
                    "data":{}
                }
            )
        return topojson

if __name__ == "__main__":
    Command().run()
