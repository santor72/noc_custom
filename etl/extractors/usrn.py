# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# UserSide Extractors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import namedtuple
import requests
from requests.auth import HTTPDigestAuth
import json
import pprint
import re
import csv
import os
from typing import Any, List, Iterable, Type, Union, Tuple, Set, Optional

# NOC modules
from noc.core.etl.extractor.base import BaseExtractor,RemovedItem
from noc.core.etl.loader.base import BaseLoader
from noc.core.etl.models.base import BaseModel
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.gis.models.geocodercache import GeocoderCache
from noc.config import config
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject as ManagedObjectNoc
from noc.inv.models.networksegment import NetworkSegment as NetworkSegmentNoc
from noc.sa.models.administrativedomain import AdministrativeDomain as AdministrativeDomainNoc
from noc.sa.models.authprofile import AuthProfile as AuthProfileNoc
from noc.sa.models.managedobjectprofile import ManagedObjectProfile as ManagedObjectProfileNoc
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile as NetworkSegmentProfileNoc
from noc.main.models.remotesystem import RemoteSystem

#etl models
from noc.core.etl.models.managedobjectprofile import ManagedObjectProfile
from noc.core.etl.models.networksegment import NetworkSegment
from noc.core.etl.models.networksegmentprofile import NetworkSegmentProfile
from noc.core.etl.models.administrativedomain import AdministrativeDomain
from noc.core.etl.models.authprofile import AuthProfile
from noc.core.etl.models.managedobject import ManagedObject


class USRNRemoteSystem(BaseRemoteSystem):
    """
    Базовый класс для Выгрузки.
    Для порядка описываем доступные для использования переменные, доступные в RemoteSystem Environment

    Configuration variables (Main -> Setup -> Remote System -> Environments)
    url - RESTAPI Userside вместе с ключом api
    """
    def extract(self,extractors=None, incremental: bool = False, checkpoint: Optional[str] = None):
        
        #Save mappings for Noc objects
        
        auprdata = [[x.name,x.id] for x in AuthProfileNoc.objects.all()]
        with open('/var/lib/noc/import/RNUserside/authprofile/mappings.csv','w') as f:
            for aupritem in auprdata:
                f.write("{0},{1}\n".format(aupritem[0],aupritem[1]))
        
        admddata = [[x.name,x.id] for x in AdministrativeDomainNoc.objects.all()]
        with open('/var/lib/noc/import/RNUserside/administrativedomain/mappings.csv','w') as f:
            for admditem in admddata:
                f.write("{0},{1}\n".format(admditem[0],admditem[1]))
        
        netsdata = [[x.name,x.id] for x in NetworkSegmentNoc.objects.all()]
        with open('/var/lib/noc/import/RNUserside/networksegment/mappings.csv','w') as f:
            for netsitem in netsdata:
                f.write("{0},{1}\n".format(netsitem[0],netsitem[1]))
        
        moprofiledata = [[x.name,x.id] for x in ManagedObjectProfileNoc.objects.all()]
        with open('/var/lib/noc/import/RNUserside/managedobjectprofile/mappings.csv','w') as f:
            for moprofileitem in moprofiledata:
                f.write("{0},{1}\n".format(moprofileitem[0],moprofileitem[1]))
        """
        us = RemoteSystem.objects.get(name = 'RNUserside')
        modata = ManagedObjectNoc.objects.filter(remote_system  = us)
        with open('/var/lib/noc/import/RNUserside/managedobject/mappings.csv','w') as f:
            for moitem in modata:
                if moitem.remote_id:
                    f.write("{0},{1}\n".format(moitem.remote_id,moitem.id))
        """ 
        super(USRNRemoteSystem, self).extract(extractors, incremental, checkpoint)
    


@USRNRemoteSystem.extractor
class USRNAuthProfileExtractor(BaseExtractor):
    name = "authprofile"  # Имя загрузчика, для которого написано извлеченине данных
    def iter_data(self,checkpoint: Optional[str] = None, **kwargs) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        for x in AuthProfileNoc.objects.all():
            yield AuthProfile(
                id=x.name,
                name=x.name,
                description=x.description,
                type=x.type,
                user=x.user,
                password=x.password,
                super_password=x.super_password,
                snmp_ro=x.snmp_ro,
                snmp_rw=x.snmp_rw
                )

@USRNRemoteSystem.extractor
class USRNManagedObjectProfileExtractor(BaseExtractor):
    name = "managedobjectprofile"  # Имя загрузчика, для которого написано извлеченине данных
    def iter_data(self,checkpoint: Optional[str] = None, **kwargs) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        for x in ManagedObjectProfileNoc.objects.all():
            yield ManagedObjectProfile(
                id = x.name,
                name = x.name,
                level = x.level
                )


@USRNRemoteSystem.extractor
class USRNAdministrativeDomainExtractor(BaseExtractor):
    name = "administrativedomain"
    def iter_data(self,checkpoint: Optional[str] = None, **kwargs) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        for x in AdministrativeDomainNoc.objects.filter(default_pool=None):
            yield AdministrativeDomain(
                id = x.name,
                name = x.name,
                parent = x.parent,
                default_pool = x.default_pool
            )

@USRNRemoteSystem.extractor
class USRNNetworkSegmentProfileExtractor(BaseExtractor):
    name = "networksegmentprofile"
    def iter_data(self,checkpoint: Optional[str] = None, **kwargs) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        for x in NetworkSegmentProfileNoc.objects.all():
            yield NetworkSegmentProfile(
                id = x.name,
                name = x.name
            )

@USRNRemoteSystem.extractor
class USRNNetworkSegmentExtractor(BaseExtractor):
    name = "networksegment"
    def iter_data(self,checkpoint: Optional[str] = None, **kwargs) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        ns = NetworkSegmentNoc.objects.all()
        for i in ns:
            yield NetworkSegment(
                    id = i.name,
                    parent= i.parent.name if i.parent else '',
                    name = i.name,
                    sibling = '',
                    profile = i.profile.name
            )


@USRNRemoteSystem.extractor
class USRNManagedObjectExtractor(BaseExtractor):
    """
    Получает массивы switch и radio через API и заполняет данными по умолчанию.
    В качестве контейнера использует узел, если он есть в маппингах загруженных контенеров.
    """
    name = "managedobject"
    model = ManagedObject
    def __init__(self, system):
        super(USRNManagedObjectExtractor, self).__init__(system)
        # self.containers = {}  # id -> path
        self.ids = set()
        self.seen_name = set()
        self.seen_ids = {}
        self.group_map = {}
        self.seen_ip = set()
        self.container_node = {}  # id -> node
        self.url = self.config.get("usurl", None)

    def iter_data(self,checkpoint: Optional[str] = None, **kwargs) -> Iterable[Union[BaseModel, RemovedItem, Tuple[Any, ...]]]:
        headers = {'Content-type': 'application/json'}
        PREFIX = config.path.etl_import
        ubnt_rx = re.compile("^Ubiquiti.+$")
        devs = {}
        cat = 'device'
        action = 'get_data'
        what = 'switch'
        rems = RemoteSystem.objects.get(id='5c5022fbc59c275b65765116')
        r = self.url+"&cat={}&action={}&object_type={}".format(cat,action,what)
        response = requests.get(r,verify=True, headers=headers)
        if (response.ok):
            switch = json.loads(response.content)
        else:
            response.raise_for_status()
        what = 'radio'
        r = self.url+"&cat={}&action={}&object_type={}".format(cat, action, what)
        response = requests.get(r,verify=True, headers=headers)
        if (response.ok):
            radio = json.loads(response.content)
        else:
            response.raise_for_status()
        what = 'olt'
        r = self.url+"&cat={}&action={}&object_type={}".format(cat, action, what)
        response = requests.get(r,verify=True, headers=headers)
        if (response.ok):
            olt = json.loads(response.content)
        else:
            response.raise_for_status()            
        devs = switch['data'].copy()
        devs.update(radio['data'])
        devs.update(olt['data'])        
        us = RemoteSystem.objects.get(name = 'RNUserside')

        for c in devs:
            dev = devs[c]
            if not dev['host']:
                continue
            if  dev['host'] == '255.255.255.255' or  dev['host'] == '0.0.0.0':
                continue
            newMO = {
                    "id" : None,
                    "name" : None,
                    "is_managed" : 1,
                    "administrative_domain" : 'usrn.default',
                    "pool" : 'default',
                    "segment" : 'usrn.default',
                    "profile" : 'Generic.Host',
                    "object_profile" : 'login',
                    "static_client_groups" : None,
                    "static_service_groups" : None,
                    "scheme" : 1,
                    "address" : None,
                    "port" : None,
                    "user" : None,
                    "password" : None,
                    "super_password" : None,
                    "snmp_ro" : None,
                    "description" : None,
                    "auth_profile" : 'login',
                    "tags" : None,
                    "tt_system" : None,
                    "tt_queue" : None,
                    "tt_system_id" : None
                    }
            
            newMO['id'] = dev['id']
            newMO['name'] = dev['host']
            newMO['description'] = dev['location']
            newMO['address'] = dev['host']
            if (ubnt_rx.match(dev['name'])):
                newMO["auth_profile"] = 'ubnt.us'
                newMO["object_profile"] = 'ubnt.us'
                newMO["scheme"] = 2
            mo = None
            mo = ManagedObjectNoc.objects.filter(remote_system  = us, remote_id = dev['id'])
            if not mo:
                mo = ManagedObjectNoc.objects.filter(address=dev['host'])
                if mo:
                    mo[0].remote_system = rems
                    mo[0].remote_id = dev['id']
                    try:
                        mo[0].save()
                    except:
                        continue
            if mo:
                newMO['description'] = mo[0].description
                newMO["pool"] = mo[0].pool.name
                newMO["administrative_domain"] = mo[0].administrative_domain.name
                newMO["segment"] = mo[0].segment.name
                newMO["profile"] = mo[0].profile.name
                newMO["object_profile"] = mo[0].object_profile.name
                newMO["auth_profile"] = mo[0].auth_profile.name if mo[0].auth_profile else 'login'
                newMO["scheme"] = mo[0].scheme
#            else:
#                continue

            yield ManagedObject(id = newMO["id"],
                    name = newMO["name"],
                    is_managed = newMO["is_managed"],
                    administrative_domain=newMO["administrative_domain"],
                    pool=newMO["pool"],
                    segment=newMO["segment"],
                    static_client_groups=[],
                    static_service_groups=[],
                    profile=newMO["profile"],
                    object_profile=newMO["object_profile"],
                    scheme=newMO["scheme"],
                    address=newMO["address"],
                    description=newMO["description"],
                    auth_profile=newMO["auth_profile"],
                    tags=[]
                    )


