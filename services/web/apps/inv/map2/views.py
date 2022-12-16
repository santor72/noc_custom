# ---------------------------------------------------------------------
# inv.map application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import threading
from typing import List, Set

# Third-party modules
from concurrent.futures import ThreadPoolExecutor, as_completed

# NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.interface import Interface
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.mapsettings import MapSettings
from noc.inv.models.link import Link
from noc.sa.models.objectstatus import ObjectStatus
from noc.fm.models.activealarm import ActiveAlarm
from noc.core.topology.segment import SegmentTopology
from noc.inv.models.discoveryid import DiscoveryID
from noc.maintenance.models.maintenance import Maintenance
from noc.core.text import alnum_key
from noc.core.pm.utils import get_interface_metrics
from noc.sa.interfaces.base import (
    ListOfParameter,
    IntParameter,
    StringParameter,
    DictListParameter,
    DictParameter,
)
from noc.core.translation import ugettext as _
from noc.core.cache.decorator import cachedmethod
from noc.services.web.apps.inv.map.views import MapApplication

tags_lock = threading.RLock()


class CustomMapApplication(MapApplication):
    """
    inv.net application
    """

    title = _("Custom Network Map")
    menu = _("Custom Network Map")
    glyph = "globe"

