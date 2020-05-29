#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 16 10:34:17 2018

@author: adrian

This script creates the values for the dropdown menus and automated completion
in the GUI to load data.
Values are fetched from the database and saved in a dictionary as .npy file

"""

# =============================================================================
# HARDCODED PARAMTERS
# =============================================================================

saveLocation = '/data/datajoint/dropdownMenu.npy'

# status message 
print('Script to create new dropdownMenu.npy file from DataJoint called:')

# =============================================================================
# IMPORTS
# =============================================================================

import numpy as np
import datajoint as dj
import os
import sys
import datetime

import login    # enter personal login information into login.py

dj.config['database.host'] = login.getIP()
dj.config['database.user'] = login.getUser()
dj.config['database.password'] = login.getPassword()
dj.conn()


from schema import mice, exp, meso,dlc


# only needed after dropping tables
#mice.schema.spawn_missing_classes()
#exp.schema.spawn_missing_classes()

# =============================================================================
# GET INFORMATION FROM DATAJOINT ABOUT THE MOUSE
# =============================================================================


# save properties for every mouse => upon selection in GUI, correct information
# can be displayed to the user
mouseDict = dict()
for tempDict in (mice.Mouse() - mice.Sacrificed() - mice.Breed()).fetch(as_dict=True):

    mouse_name = tempDict['mouse_name']
    mouse = mice.Mouse() & 'mouse_name = "%s"' % mouse_name
    mouseDict[ mouse_name ] = tempDict    # saves all information of the table
    surgery_type = list((mice.Surgery() & 'mouse_name = "%s"' % tempDict['mouse_name']).fetch('surgery_type'))
    startDate = mouse.get_starting_date()
    currentDay = mouse.get_current_day()
    # find date of last experiment
    if mouse.get_session_increment() == 0:
        lastExperiment = None
    else:
        lastSession = (exp.Session() & mouse) & 'session_increment = %d' % (mouse.get_session_increment()-1)
        lastExperiment = lastSession.fetch('doe')[0]

    mouseDict[ mouse_name]['startDate'] = startDate
    mouseDict[ mouse_name]['day'] = currentDay
    mouseDict[ mouse_name]['lastExperiment'] = lastExperiment
    mouseDict[ mouse_name]['surgery_type'] = surgery_type

# The GUI requires a list of strings => convert list of int to str
rigAsString = list(exp.Rig().fetch('rig_id'))
for index, elem in enumerate(rigAsString):
    rigAsString[index] = str(elem)

# get information about the optogenetics
orderedDict = exp.Optogenetics().fetch(as_dict=True)
optogenetics_dict = dict()

for entry in orderedDict:
    # save dict under the key of the primary key
    # like this the entry of the table can be recoverd by looking for the
    # primary key in the dictionary
    optogenetics_dict[ entry['opto_name'] ] = entry


# =============================================================================
# ENTER DATAJOINT DATA INTO STRUCT
# =============================================================================

dataForGui = {'Mouse':
                  list((mice.Mouse() - mice.Sacrificed() - mice.Breed()).fetch('mouse_name')),
              'MouseDict':
                  mouseDict,
              'Experimenter':
                  list(exp.Experimenter().fetch('experimenter_name')),
              'Anesthesia':
                  list(exp.Anesthesia().fetch('anesthesia_name')),
              'Rig':
                  rigAsString,
              'OptogeneticsRegion':
                  list(exp.OptogeneticsRegion().fetch('opto_region_name')),
              'OptogeneticsTiming':
                  list(exp.OptogeneticsTiming().fetch('opto_timing_name')),
              'OptogeneticsVariant':
                  list(exp.OptogeneticsVariant().fetch('opto_variant_name')),
              'Optogenetics':
                  list(exp.Optogenetics().fetch('opto_name')),
              'Optogenetics_dict':
                  optogenetics_dict,
              'ForceField':
                  list(exp.ForceField().fetch('force_field_name')),
              'ForceField_Strength':
                  list(exp.ForceField().fetch('strength')),
              'Task':
                  list(exp.Task().fetch('task_name')),
              'Task_Details':
                  list(exp.Task().fetch('task_details')),
              'Joystick':
                  list(exp.Joystick().fetch('joystick_name')),
              'TimeStamp':
                  datetime.datetime.now(),
              'SurgeryType': 
                  list(mice.SurgeryType().fetch('surgery_type'))
             }
# =============================================================================
# GET INFORMATION ABOUT MESOCOPE DATA
# =============================================================================

# get contents of scan_details
orderedDict = meso.ScanDetails().fetch(as_dict=True)
scan_details_dict = dict()

for entry in orderedDict:
    # save dict under the key of the primary key
    scan_details_dict[ entry['scan_details'] ] = entry

# enter the rest of the meso data into the dictionary
mesoDict = dict(software = meso.Software().fetch('software'),
                brain_region = meso.BrainRegion().fetch('brain_region'),
                layer = meso.Layer().fetch('layer'),
                compartment = meso.Compartment().fetch('compartment'),
                fluorophore = meso.Fluorophore().fetch('fluorophore'),
                scan_details = meso.ScanDetails().fetch('scan_details'),
                scan_details_dict = scan_details_dict,
                aim = meso.Aim().fetch('aim')
                )

# add dict to the data for the GUI
dataForGui['meso_dict'] = mesoDict


# =============================================================================
# GET INFORMATION ABOUT DEEPLABCUT MODEL
# =============================================================================
# get contents of model
#orderedDict = dlc.ModelVersion().fetch(as_dict=True)
#model_details_dict = dict()

#for entry in orderedDict:
    # save dict under the key of the primary key
#    model_details_dict[ entry['model_id'] ] = entry

# enter the rest of the meso data into the dictionary
#modelDict = dict(model_id=dlc.ModelVersion().fetch('model_id'),
#                path_of_config_file = dlc.ModelVersion().fetch('path_of_config_file'),
#                iteration = dlc.ModelVersion().fetch('iteration'),
#                shuffle =dlc.ModelVersion().fetch('shuffle'),
#                )

# add dict to the data for the GUI
#dataForGui['model_dict'] = modelDict#orderedDict#modelDict



# =============================================================================
# SAVE THE FILE
# =============================================================================

np.save( saveLocation, dataForGui)

print('    Updated dropdownMenu.npy file saved')
