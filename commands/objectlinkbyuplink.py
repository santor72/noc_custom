from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.link import Link
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.management.base import BaseCommand

import time
import os
import json
import requests
import re
from typing import List, Union, Dict


class Command(BaseCommand):
    api_name = "customermap"
    openapi_tags = ["customermap API"]
    usurl="http://usrn.ccs.ru//api.php?key=weifdovIpyirdyilyablichhyasgojyatwejIkKenvaitnajal"
    profiles = []

    def getnode(self, dev_type, dev_id):
        response = requests.get(f"{self.usurl}+&cat=device&action=get_data&object_type={dev_type}&object_id={dev_id}")
        if(response.ok):
            data = json.loads(response.content)
            return data['data'].get(str(dev_id))
        else:
            return {}
    
    def get_links(self, dev_type, dev_id, nodes, links):
        response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type={dev_type}&object_id={dev_id}")
        if(response.ok):
            data = json.loads(response.content)
            if data['Result'] == 'OK':
                for k in data['data']:
                    if not k in nodes[dev_id].get('uplink_ifaces'):
                        continue
                    for item in data['data'][k]:
                        if item['connect_id'] in links:
                            continue
                        if item['object_type']=='switch' or item['object_type']=='radio':
                            if item['object_id'] in nodes:
                                devdata = nodes[item['object_id']]
                                ifaces = devdata.get('ifaces')
                                uplink_ifaces = devdata.get('uplink_iface_array')
                            else:
                                devdata = self.getnode(item['object_type'], item['object_id'])                        
                                ifaces = devdata.get('ifaces')
                                uplink_ifaces = devdata.get('uplink_iface_array')
                                nodes[item['object_id']] = {'id': item['object_id'],
                                                            'type':item['object_type'],
                                                            'nazv': devdata.get('nazv'),
                                                            'location': devdata.get('location'),
                                                            'uzelcode': devdata.get('uzelcode'),
                                                            'host': devdata.get('host'),
                                                            'ip': devdata.get('host'),
                                                            'ifaces': ifaces,
                                                            'uplink_ifaces': uplink_ifaces
                                                            }
                            ifnum =  item.get('interface')
                            links[item['connect_id']]={
                                'id':item['connect_id'],
                                'nodea': dev_id,
                                'nodeb':item['object_id'],
                                'inta':nodes[dev_id]['ifaces'].get(k),
                                'intb': ifaces.get(str(ifnum))
                                }
                            if (devdata.get('host')!='217.76.46.108' and devdata.get('host')!='217.76.46.119' and devdata.get('host')!='10.76.33.82'):
                                self.get_links(item['object_type'], item['object_id'], nodes, links)

    def findnodebyip(self, nodes,ip):
        for x in nodes.keys():
            if nodes[x].get('ip'):
                return x
        return 0

    def findlink(self, nodes,links,link):
        ip_a=nodes[link['nodea']].get('ip')
        ip_b=nodes[link['nodeb']].get('ip')
        int_a = link['inta']['ifIndex']
        int_b = link['intb']['ifIndex']
        for k,v in links.items():
            a_ip = nodes[v['nodea']].get('ip')
            b_ip = nodes[v['nodeb']].get('ip')
            a_int = v['inta']['ifIndex']
            b_int = v['intb']['ifIndex']
            if ip_a in [a_ip, b_ip] and ip_b in [a_ip, b_ip]:
                if int_a in [b_int, a_int] and int_b in [a_int, b_int]:
                    return 1
        return 0

    def nocaddnode(self,nodes,mo):
        if not self.findnodebyip(nodes, mo.address):
            newid = f"noc{mo.id}"
            nodes[newid] = {
                'id' : newid,
                'ip' : mo.address,
                'host': mo.address,
                'type': 'switch',
                'location': mo.description,
                'nazv': mo.name
            }
            return 1
        return 0

    def nocgetlinks(self, nodes, links, moid):
        if not self.profiles:
            iprofiles = InterfaceProfile.objects.filter(name__contains='Uplink')
            iprofiles2 = InterfaceProfile.objects.filter(name__contains='Core')
            self.profiles = [x for x in iprofiles] + [x for x in iprofiles2]
        mo_links=[]
        mo_alllinks = Link.objects.filter(linked_objects__in=[moid])
        mointerfaces= Interface.objects.filter(managed_object__in=[moid], profile__in=[x.id for x in self.profiles])
        for i in mointerfaces:
            for l in mo_alllinks:
                monext = 0 
                if i.id == l.interfaces[0].id:
                    isnew = self.nocaddnode(nodes,l.interfaces[1].managed_object)
                    nodea=self.findnodebyip(nodes, l.interfaces[0].managed_object.address)
                    nodeb=self.findnodebyip(nodes, l.interfaces[1].managed_object.address)
                    link = {
                        'id' : str(l.id),
                        'nodea' : nodea,
                        'nodeb' : nodeb,
                        'inta' : {'ifIndex': l.interfaces[0].ifindex,
                                'ifName': l.interfaces[0].name,
                                'ifNumber': l.interfaces[0].ifindex,
                                'ifType': 6
                                },
                        'intb' : {'ifIndex': l.interfaces[1].ifindex,
                                'ifName': l.interfaces[1].name,
                                'ifNumber': l.interfaces[1].ifindex,
                                'ifType': 6
                                }                                
                    }
                    if not self.findlink(nodes, links, link):                
                        links[link['id']] = link
                    if isnew:
                        nocgetlinks(nodes,links,l.interfaces[1].managed_object.id)
                elif i.id == l.interfaces[1].id:
                    isnew = self.nocaddnode(nodes,l.interfaces[0].managed_object)
                    nodea=self.findnodebyip(nodes, l.interfaces[1].managed_object.address)
                    nodeb=self.findnodebyip(nodes, l.interfaces[0].managed_object.address)
                    link={
                        'id': str(l.id),
                        'nodea' : nodea,
                        'nodeb' : nodeb,
                        'inta' : {'ifIndex': l.interfaces[1].ifindex,
                                'ifName': l.interfaces[1].name,
                                'ifNumber': l.interfaces[1].ifindex,
                                'ifType': 6
                                },
                        'intb' : {'ifIndex': l.interfaces[0].ifindex,
                                'ifName': l.interfaces[0].name,
                                'ifNumber': l.interfaces[0].ifindex,
                                'ifType': 6
                                }                                
                    }
                    if not self.findlink(nodes, links, link):                
                        links[link['id']] = link
                    if isnew:
                        nocgetlinks(nodes,links,l.interfaces[0].managed_object.id)
        return 0

    def asknoc(self,nodes,links):
        for node in nodes:
            MOs = ManagedObject.objects.filter(address=nodes[node].get('ip'))
        if MOs:
            mo = MOs[0]
            self.nocgetlinks(nodes,links, mo.id)
        
    def handle(self, *args, **options):
        result = {}
        nodes={}
        links={}
        customer={}
        connect()
        customer_id=6288
        a_response = requests.get(f"{self.usurl}&cat=customer&action=get_data&customer_id={customer_id}")
        if a_response.ok:
            customer=json.loads(a_response.content)
            if customer['Result'] != 'OK':
                result={'Result':'Fail', 'message': 'Customer not found'}
                return JSONResponse(content=result, media_type="application/json")
        else:
            result={'Result':'Fail', 'message': 'Customer find error'}
            return JSONResponse(content=result, media_type="application/json")
        nodes[customer_id] = {}
        nodes[customer_id] = {'id': customer_id, 
                      'type': 'customer',
                      'host':customer['Data']['login'],
                      'ip': customer['Data']['ip_mac'],
                      'location': customer['Data']['login'],
                      'nazv': customer['Data']['login']
                     }
        ac_response = requests.get(f"{self.usurl}&cat=commutation&action=get_data&object_type=customer&object_id={customer_id}")
        if(ac_response.ok):
            ac_data = json.loads(ac_response.content)
            if ac_data['Result'] == 'OK':
                for ac_item in ac_data['data']:
                    if ac_item['object_type']=='switch' or ac_item['object_type']=='radio':
                        devdata = self.getnode(ac_item['object_type'], ac_item['object_id'])
                        ifnum =  ac_item.get('interface')
                        ifaces = devdata.get('ifaces')
                        uplink_ifaces = [x for x in devdata.get('uplink_iface_array')]
                        ifname=''
                        if ifnum:
                            if ifaces.get(ifnum):
                                ifname = ifaces[ifnum].get('ifName')
                        links[ac_item['connect_id']]={'id':ac_item['connect_id'], 'nodea': customer_id,'inta':{'ifIndex': 1,
                                                                                                            'ifType': 1,
                                                                                                            'ifName': 'C',
                                                                                                            'ifNumber': 1},
                                                    'nodeb':ac_item['object_id'], 'intb': ifaces.get(str(ifnum))}
                        nodes[ac_item['object_id']] = {'id': ac_item['object_id'],
                                                    'type':ac_item['object_type'],
                                                    'nazv': devdata.get('nazv'),
                                                    'location': devdata.get('location'),
                                                    'uzelcode': devdata.get('uzelcode'),
                                                    'host': devdata.get('host'),
                                                    'ip': devdata.get('host'),
                                                    'ifaces': ifaces,
                                                    'uplink_ifaces': uplink_ifaces
                                                    }
                        self.get_links(ac_item['object_type'], ac_item['object_id'], nodes, links)
            else:
                result={'Result':'Fail', 'message': 'Fail find customer commutation'}
                return JSONResponse(content=result, media_type="application/json")                                        
        else:
            result={'Result':'Fail', 'message': 'Fail request customer commutation'}
            return JSONResponse(content=result, media_type="application/json")  
        self.asknoc(nodes,links)
        topology_dict = {'nodes': [], 'links': []}
        for k,item in nodes.items():
            topology_dict['nodes'].append({
                'id': str(item['id']),
                'name': 'MSK-IX' if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82'] else item.get('host'),
                'primaryIP': item.get('host') or item.get('ip'),
                'nazvanie': item.get('nazv'),
                'location': item.get('location'),
                'icon': 'host' if item['type'] == 'customer' else ('cloud' if item.get('ip') in ['217.76.46.108','217.76.46.119','10.76.33.82'] else 'switch')
            })
        for k,item in links.items():
            topology_dict['links'].append({
                'id': str(item['id']),
                'source': str(item['nodea']),
                'target': str(item['nodeb']),
                'srcIfName': item['inta']['ifName'],
                'tgtIfName': item['intb']['ifName'],
                'srcDevice': str(item['nodea']),
                'tgtDevice': str(item['nodeb'])
            })                          
        result=topology_dict
        #with open('/root/topotemp.json','w') as f:
        #    json.dump(result,f)
        from pprint import pprint
        pprint(nodes)
#        pprint(links)

if __name__ == "__main__":
    Command().run()

