#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 19:28:43 2019

@author: tanmay
"""

import deeplabcut
import datajoint as dj
import login

# log in to database
dj.config['database.host'] = login.getIP()
dj.config['database.user'] = login.getUser()
dj.config['database.password'] = login.getPassword()
dj.conn()


from schema import dlc

# CALL POPULATE METHODS

dlc.DeepLabCut().populate()
dlc.DeepLabCut3D().populate()




