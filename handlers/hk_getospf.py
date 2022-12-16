# coding: utf-8
#python modules
import re
from pprint import pprint
import pickle
import copy

#NOC modules
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.custom.lib.ospf import *

def hk_getospf_handler(djob):
    mo: "ManagedObject" = djob.object
    if mo.profile.name.replace('.','_')+'_get_ospf_peers_all' in globals():
        