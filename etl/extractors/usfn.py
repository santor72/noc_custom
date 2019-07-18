# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Zabbix Extractors
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


# NOC modules
from noc.core.etl.extractor.base import BaseExtractor
from noc.core.etl.remotesystem.base import BaseRemoteSystem
from noc.gis.models.geocodercache import GeocoderCache
from noc.config import config
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.sa.models.authprofile import AuthProfile
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.main.models.remotesystem import RemoteSystem


class USRNRemoteSystem(BaseRemoteSystem):
    """
    Базовый класс для Выгрузки.
    Для порядка описываем доступные для использования переменные, доступные в RemoteSystem Environment

    Configuration variables (Main -> Setup -> Remote System -> Environments)
    url - RESTAPI Userside вместе с ключом api
    """


@USRNRemoteSystem.extractor
class USRNContainerExtractor(BaseExtractor):
    """
    Извлекает узлы связи. Заносит их в как PoP | Access
    помещая в контейнер Global Lost&Found
    """
    name = "container"  # Имя загрузчика, для которого написано извлеченине данных

    def __init__(self, system, config=None, containers=None, container_node=None):
        super(USRNContainerExtractor, self).__init__(system)
        self.containers = containers
        self.container_node = container_node
        self.url = self.config.get("usurl", None)

    def extract(self):
        super(USRNContainerExtractor, self).extract()
        

    def extract_data(self):
        super(USRNContainerExtractor, self).extract()

    def iter_data(self):
        model = "PoP | Access"  # Модель объекта. POP | Access - точка присутствия
        headers = {'Content-type': 'application/json'}
        cat = 'node'
        action = 'get'
        what = 0
        r = self.url+"&cat={}&action={}&object_type={}".format(cat,action,what)
        response = requests.get(r,verify=True, headers=headers)
        if (response.ok):
            containers = json.loads(response.content)
        else:
            response.raise_for_status()
        for c in containers['data']:
            container = containers['data'][c]
            cid = container['id']
            name = '{} - {}'.format(container['number'], container['name'])
            lat = None
            lon = None
            path= 'Global Lost&Found'
            if ('coordinates' in container):
                if ('lat' in container['coordinates'] and 'lon' in container['coordinates']):
                    lat = container['coordinates']['lat']
                    lon = container['coordinates']['lon']
            yield [
                    cid,
                    name,
                    model,
                    path,
                    0,
                    lon,
                    lat,
                    container['location']
            ]


    """
    Выгружаем существующие в noc сущности
    """

@USRNRemoteSystem.extractor
class USRNAuthProfileExtractor(BaseExtractor):
    name = "authprofile"  # Имя загрузчика, для которого написано извлеченине данных
    data = [[x.name,x.name,x.description,x.type,x.user,x.password,x.super_password,x.snmp_ro,x.snmp_rw] for x in AuthProfile.objects.all()]


@USRNRemoteSystem.extractor
class USRNManagedObjectProfileExtractor(BaseExtractor):
    name = "managedobjectprofile"  # Имя загрузчика, для которого написано извлеченине данных
    data =  [[x.name,x.name,x.level] for x in ManagedObjectProfile.objects.all()]


@USRNRemoteSystem.extractor
class USRNAdministrativeDomainExtractor(BaseExtractor):
    name = "administrativedomain"
    data = [[x.name,x.name,x.parent,x.default_pool] for x in AdministrativeDomain.objects.filter(default_pool=None)]


@USRNRemoteSystem.extractor
class USRNNetworkSegmentProfileExtractor(BaseExtractor):
    name = "networksegmentprofile"
    data = [[x.name,x.name] for x in NetworkSegmentProfile.objects.all()]

@USRNRemoteSystem.extractor
class USRNNetworkSegmentExtractor(BaseExtractor):
    name = "networksegment"
    def iter_data(self):
        ns = NetworkSegment.objects.all()
        for i in ns:
            fields ={ 
                    "id" : i.name,
                    "parent" : '',
                    "name" : i.name,
                    "sibling" : '',
                    "profile" : i.profile.name
                    }
            if i.parent != None:
                fields["parent"] = i.parent.name
            yield [
                    fields["id"],
                    fields["parent"],
                    fields["name"],
                    fields["sibling"],
                    fields["profile"]
                    ]


@USRNRemoteSystem.extractor
class USRNManagedObjectExtractor(BaseExtractor):
    """
    Получает массивы switch и radio через API и заполняет данными по умолчанию.
    В качестве контейнера использует узел, если он есть в маппингах загруженных контенеров.
    """
    name = "managedobject"

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

    def iter_data(self):
        headers = {'Content-type': 'application/json'}
        PREFIX = config.path.etl_import
        import_dir = os.path.join(PREFIX,'RNUserside','container')
        mappings_path = os.path.join(import_dir,"mappings.csv")
        container_mappings={}
        ubnt_rx = re.compile("^Ubiquiti.+$")
        devs = {}
	# Считываем данные о контейнерах
        with open(mappings_path) as f:
            reader = csv.reader(f)
            for k, v in reader:
                container_mappings[k] = v
        cat = 'device'
        action = 'get_data'
        what = 'switch'
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
            
        devs = switch['data'].copy()
        devs.update(radio['data'])
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
                    "container" : None,
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
            us_uzel = '{}'.format(dev['uzelcode'])
	    """
	    Проверяем модель в Юзерсайд, если это Ubnt выставляем 
	    специфические профили и доступ по SSH
	    """
            if (ubnt_rx.match(dev['name'])):
                newMO["auth_profile"] = 'ubnt.us'
                newMO["object_profile"] = 'ubnt.us'
                newMO["scheme"] = 2
            if us_uzel in container_mappings:
                newMO['container'] = us_uzel
            mo = None
            mo = ManagedObject.objects.filter(remote_system  = us, remote_id = dev['id'])
            if mo:
                newMO['description'] = mo[0].description
                newMO["pool"] = mo[0].pool
                newMO["administrative_domain"] = mo[0].administrative_domain
                newMO["segment"] = mo[0].segment
                newMO["profile"] = mo[0].profile
                newMO["object_profile"] = mo[0].object_profile
                newMO["auth_profile"] = mo[0].auth_profile
                newMO["scheme"] = mo[0].scheme

            yield [ 
                    newMO["id"],
                    newMO["name"],
                    newMO["is_managed"],
                    newMO["container"],
                    newMO["administrative_domain"],
                    newMO["pool"],
                    newMO["segment"],
                    newMO["profile"],
                    newMO["object_profile"],
                    newMO["static_client_groups"],
                    newMO["static_service_groups"],
                    newMO["scheme"],
                    newMO["address"],
                    newMO["port"],
                    newMO["user"],
                    newMO["password"],
                    newMO["super_password"],
                    newMO["snmp_ro"],
                    newMO["description"],
                    newMO["auth_profile"],
                    newMO["tags"],
                    newMO["tt_system"],
                    newMO["tt_queue"],
                    newMO["tt_system_id"]
                    ]


    def extract(self):
        super(USRNManagedObjectExtractor, self).extract()  # Запуск извлечения ManagedObject
