import requests
from requests.auth import HTTPDigestAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
from pprint import pprint
import re

def getcustomer(usurl,login):
#    usurl='http://usrn.ccs.ru//api.php?key=weifdovIpyirdyilyablichhyasgojyatwejIkKenvaitnajal'
    usabonidjson = requests.get(usurl+'&cat=customer&subcat=get_abon_id&data_typer=login&data_value='+login)
    if(usabonidjson.ok):
        usaboniddata = json.loads(usabonidjson.content)
    else:
        result = None
    if usaboniddata['Result'] == 'OK':
        result=usaboniddata['Id']
    else:
        result=None
    return result

def getdevices(usurl,customer_id):
    commjson=requests.get(usurl+'&cat=commutation&action=get_data&object_type=customer&object_id='+str(customer_id))
    if(commjson.ok):
        commdata = json.loads(commjson.content)
    else:
        result = None    
    if commdata['Result'] == 'OK':
        data=[]
        prev_device_id=0
        devicedata={}
        for i in commdata['data']:            
            if i['object_id']==prev_device_id:
                data.append({
                    'id': i['object_id'],
                    'host': devicedata['data'][str(i['object_id'])]['host'],
                    'interface': i['interface']
                })
                continue
            devicejson = requests.get(usurl+'&cat=device&action=get_data&is_hide_ifaces_data=0&object_type='+i['object_type']+'&object_id='+str(i['object_id']))
            if(devicejson.ok):
                devicedata = json.loads(devicejson.content)
            else:
                result = None
            if devicedata['Result'] == 'OK':
                #pprint(devicedata)
                data.append({
                    'id': i['object_id'],
                    'host': devicedata['data'][str(i['object_id'])]['host'],
                    'interface': i['interface'],
                    'ifname': devicedata['data'][str(i['object_id'])]['ifaces'][str(i['interface'])]['ifName']
                })
            else:
                result=None
        result = data
    else:
        result=None
    return result    

