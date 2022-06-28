import json
import requests
from requests.auth import HTTPDigestAuth
import re
import datetime

headers = {'Content-type': 'application/json'}
class obj3CX:
    Cookies = None
    def __init__(self,user=None, passwd=None, url=None):
       self.user = user
       self.passwd = passwd
       self.pbxurl = url
       
    def __del__(self):
        if self.Cookies:
            self.logout()

    def logout(self):
        if self.Cookies:
                request = self.pbxurl + '/api/logout'
                response = requests.get(request,verify=False, cookies=self.Cookies , headers=headers)
                
    def login(self):
        request = self.pbxurl + '/api/login'
        query = {"Username": self.user, "Password": self.passwd}
        res = False
        try:
            #Login to PBX
            if self.Cookies:
                self.logout()
            response = requests.post(request,verify=False, data=json.dumps(query), headers=headers)
            if(response.ok):
                self.Cookies = {'.AspNetCore.Cookies' : response.cookies['.AspNetCore.Cookies']}
                res = True
            else:
                res = False
        except:
            Cookies = None
            res = False
        finally:
            return res

        
    def active_calls(self):
        res = {}
        try:
            #check Login to PBX
            if not self.Cookies:
                if not self.login():
                    res['failed'] = True
                    res['result'] = 'login error'
                    return res
            #Get current active calls
            request = self.pbxurl + '/api/ActiveCalls'
            response_calls = requests.get(request,verify=False, cookies=self.Cookies , headers=headers)
            if(response_calls.ok):
                result_calls = json.loads(response_calls.content)
                res['failed'] = False
                res['result'] = result_calls['list']
            else:
                res['failed'] = True
                res['result'] = 'Error get active calls list'
        except:
            res['failed'] =  True
            res['result'] = 'Exception'
        finally:
            return res
        
    def calls_logs(self,dateRangeType='Today', callState='Any'):
        res = {}
        HasMoreRows = True
        startrow = 0
        try:
            #check Login to PBX
            if not self.Cookies:
                if not self.login():
                    res['failed'] = True
                    res['result'] = 'login error'
                    return res
            #Get calls records
            #url = `/api/CallLog?TimeZoneName=${filterParams.TimeZoneName}&callState=${filterParams.callState}&dateRangeType=${filterParams.dateRangeType}
            #&fromFilter=${filterParams.fromFilter}&fromFilterType=${filterParams.fromFilterType}&numberOfRows=${filterParams.numberOfRows}
            #&searchFilter=${filterParams.searchFilter}&startRow=${filterParams.startRow}
            #&toFilter=${filterParams.toFilter}&toFilterType=${filterParams.toFilterType}`
            #result_calls['CallLogRows']
            #HasMoreRows
            temp = []
            while HasMoreRows:
                request = self.pbxurl + f"/api/CallLog?TimeZoneName=Europe%2FMoscow&callState={callState}&dateRangeType={dateRangeType}&fromFilter=&fromFilterType=Any&numberOfRows=50&searchFilter=&startRow={startrow}&toFilter=&toFilterType=Any"
                response_calls = requests.get(request,verify=False, cookies=self.Cookies , headers=headers)
                if(response_calls.ok):
                    result_calls = json.loads(response_calls.content)
                    res['failed'] = False
                    temp = temp + result_calls['CallLogRows']
                    HasMoreRows = result_calls['HasMoreRows']
                    startrow = startrow + len(result_calls['CallLogRows'])
                else:
                    raise Exception('Error get active calls list')
            offset = datetime.timedelta(hours=3)
            tz = datetime.timezone(offset, name='МСК')
            for item in temp:
                date_time_str = (re.findall(r"^\d{4}-\d{2}-\d{2}T\d{2}",
                                            item['CallTime']))[0]
#                date_time_str = date_time_str.replace('T',' ') + ':00:00'
#                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
                date_time_obj = datetime.datetime.strptime(item['CallTime'], '%Y-%m-%dT%H:%M:%S%z')
                item['ts'] = int(date_time_obj.timestamp())
                item['date']= date_time_obj
            res['result'] = temp
        except Exception as e:
            res['failed'] =  True
            res['result'] = 'Exception'
            res['e'] = e
        finally:
            return res
    
