# ---------------------------------------------------------------------
# Vendor: Angtel (Angstrem telecom - http://www.angtel.ru/)
# OS:     Topaz
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Topaz.Topaz"

    pattern_unprivileged_prompt = rb"^.+\(.+\)>"
    pattern_prompt = rb"^.+\(.+\)>"
    command_exit = "exit"

