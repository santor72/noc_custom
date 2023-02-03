 coding: utf-8
#python modules
import re
from pprint import pprint
import pickle
import copy

#NOC modules
from noc.core.mongo.connection import connect
from noc.sa.models.managedobject import ManagedObject
from noc.custom.lib.ospf import *

def hk_test_handler(djob):
    return ['show ver']
