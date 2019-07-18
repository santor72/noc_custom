import requests
from requests.auth import HTTPDigestAuth
import json
from pprint import pprint
import re
from noc.main.models.remotesystem import RemoteSystem

def zte_search_onu(s):
    query = {
        'key': apikey,
        'cat' : 'device',
        'action' : 'get_data',
        'object_type' : 'onu',
        'serial' : s
    }
    r =  apiurl_rn + '&'.join(['{}={}'.format(y,query[y]) for y in query.keys()])
    response = requests.get(r,verify=True, headers=headers)
    if (response.ok):
        res = json.loads(response.content)
        if (res['Result'] == 'OK'):
            return res['data'][list(res['data'].keys())[0]]
        else:
            return None
    else:
        response.raise_for_status()

def bdcom_search_onu(mac):
    query = {
        'key': apikey,
        'cat' : 'device',
        'action' : 'get_data',
        'object_type' : 'onu',
        'mac' : mac
    }
    r =  apiurl_rn + '&'.join(['{}={}'.format(y,query[y]) for y in query.keys()])
    response = requests.get(r,verify=True, headers=headers)
    if (response.ok):
        res = json.loads(response.content)
        if (res['Result'] == 'OK'):
            return res['data'][list(res['data'].keys())[0]]
        else:
            return None
    else:
        response.raise_for_status()


us = RemoteSystem.objects.get(name = 'RNUserside')
apikey = us.config.get("apikey", None)
apiurl = us.config.get("apiurl", None)
apiurl_rn = us.config.get("apiurl_rn", None)
#pp = pprint.PrettyPrinter(indent=4, depth=1)
headers = {'Content-type': 'application/json'}
#url = ''

cat = 'usm_pon'
action = 'get_devices'

r = apiurl+"key={}&cat={}&action={}".format(apikey,cat,action)
response = requests.get(r,verify=True, headers=headers)
if (response.ok):
    devs = json.loads(response.content)
else:
    response.raise_for_status()

query = {
    'key': apikey,
    'cat' : 'device',
    'action' : 'get_data',
    'object_type' : 'switch',
    'object_id' : devs['DevicesList']
}
r =  apiurl + '&'.join(['{}={}'.format(y,query[y]) for y in query.keys()])
response = requests.get(r,verify=True, headers=headers)
if (response.ok):
    olts = json.loads(response.content)['data']
else:
    response.raise_for_status()

re_ok = re.compile('^{"Result":"OK".+')
query = {
    'key': apikey,
    'cat' : 'usm_pon',
    'action' : 'list_onu',
    'device_id' : ''
}
onus={}
for k in olts.keys():
    onus_temp = {}
    query['device_id'] = k
    r = apiurl_rn + '&'.join(['{}={}'.format(y,query[y]) for y in query.keys()])
    response = requests.get(r,verify=True, headers=headers)
    if (response.ok and response.content):
        onus_temp = json.loads(response.content)['onulist']
        if len(onus_temp) > 0:
          onus[k] = onus_temp
    else:
        response.raise_for_status()

onu_not_in_us = dict.fromkeys(olts.keys(),{})
re_zte = re.compile("^ZTE.+$")
re_bdcom = re.compile("^BDCOM.+$")
notlist = []
for k in onus.keys():
    tmp = {}
    tmp2 = {}
    if (re_zte.match(olts[k]['name'])):
        for o in onus[k].keys():
            onu = zte_search_onu(onus[k][o]['id'])
            if not onu:
                tmp[o]=onus[k][o]
                notlist.append({'id':onus[k][o]['id'], 'mac' : '', 'model' : onus[k][o]['model'], 'vendor': onus[k][o]['vendor'], 'iface' : onus[k][o]['ifaceName']})
    if (re_bdcom.match(olts[k]['name'])):
        for o in onus[k].keys():
            onu = bdcom_search_onu(onus[k][o]['mac'])
            if not onu:
                tmp[o]=onus[k][o]
                notlist.append({'mac':onus[k][o]['mac'], 'id' : '', 'model' : onus[k][o]['model'], 'vendor': onus[k][o]['vendor'], 'iface' : onus[k][o]['ifaceName']})
    onu_not_in_us[k] = tmp
pprint(notlist)
