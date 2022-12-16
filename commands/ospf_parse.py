#python modules
import re
from pprint import pprint
import pickle
import json
#NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.core.mongo.connection import connect

class OSPF_Topo:
    raw = {}
    links=[]
    js={}

    def getmo(self,ip):
        mo = ManagedObject.objects.filter(address = ip)
        if mo:
            return mo[0]
        else:
            return None
    def makelinks(self):
        for k,v in self.raw.items():
            for peeritem in v['peers']:
                link = {
                    'area': peeritem['area'],
                    'node1_id': v['id'],
                    'node1_bi': k, 
                    'node1_int': peeritem['interface'],
                    'node2_id': peeritem['peer_id'],
                    'node2_bi': '', 
                    'node2_int': '',                    
                }
                peer_mo = self.getmo(peeritem['peer_id'])
                if peer_mo:
                    link['node2_bi'] = peer_mo.bi_id
                    if peer_mo.bi_id in list(self.raw.keys()):
                        for peer_peeritem in self.raw[peer_mo.bi_id]['peers']:
                            if peer_peeritem['peer_id'] == v['id']:
                                link['node2_int'] = peer_peeritem['interface']
                self.links.append(link)

    def js_set_group(self, ip, area):
        for node in self.js['nodes']:
            if node['id'] == ip:
                if node['group'] != '0.0.0.0' or area == '0.0.0.0':
                    node['group'] = area
    
    def makejs(self):
        n = []
        self.js['nodes'] = []
        self.js['edges'] = []
        self.js['groups'] = ['others', '0.0.0.0']
        for k,v in self.raw.items():
            if k == 'routers':
                continue
            if not v['id'] in n:
                n.append(v['id'])
                self.js['nodes'].append({ 'id': v['id'], 'type': 'server', 'label': v['id'], 'group': 'others'})
            for v1 in v['peers']:
                if not v1['peer_id'] in n:
                    n.append(v1['peer_id'])
                    self.js['nodes'].append({ 'id': v1['peer_id'], 'type': 'server', 'label': v1['peer_id'], 'group': 'others'})
                if (not v1['area'] in self.js['groups']) and not (v1['area'] in ['0','0.0.0.0']):
                    self.js['groups'].append(v1['area'])
                self.js_set_group(v1['peer_id'], '0.0.0.0' if v1['area'] == '0' else v1['area'])
                y = 0
                for i in self.js['edges']:
                    if i['source'] == v['id'] and i['target'] == v1['peer_id']:
                        i['label'] = i['label'] + 1
                        y = 1
                        break
                    if i['source'] == v1['peer_id'] and i['target'] == v['id']:
                        i['label'] = i['label'] + 1
                        y = 1
                        break
                if y == 1:
                    continue
                self.js['edges'].append({
                    'source': v['id'],
                    'target': v1['peer_id'],
                    'label': 1
                })


#connect()
topology = OSPF_Topo()
with open('/tmp/ospf_topo.pickle', 'rb') as f:
         data = pickle.load(f)
topology.raw = data['16143']
#topology.makelinks()
topology.makejs()
s = json.dumps(topology.js)
with open('/tmp/ospf_topo.js', 'w') as f2:
    f2.write('const elements = ' + s+';\r\n')
    f2.write("Diagram('scheme1', elements);\r\n")