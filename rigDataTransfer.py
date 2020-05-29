#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 12:51:59 2018

@author: tanmay, modified by adrian

This script opens a GUI that lets the user enter data about an experiment
performed at one of the rigs.
Entries for the dropdown menus are added by loading a .npy dictionary with
previously fetched data from DataJoint.
Once the user hits "submit", the selected files will be pushed to the database
and a .npy dictionary with all entered data is also transfered to the server.
"""
# =============================================================================
# HARDCODED PATHS
# =============================================================================

savePathForNpy = '/data/tmp/'
savePathForData = '/data/rawdata/'
dropDownMenuFile = '/data/datajoint/dropdownMenu.npy'

sshAddress = "mathislab@10.170.0.42:"


defaultExperimenter = 'mackenzie'
defaultRigString = '1'
defaultJoystick = 'classical'
defaultTask = 'baseline'
defaultOptoVariant = 'none'
# add more default values here if necessary

## TODO:
    # add selecting optogenetics (like scan_details in meso), at the moment disabled

# =============================================================================
# IMPORTS
# =============================================================================

import wx
import os
import numpy as np
import arrow
import datetime
import re
#import 


# copy file from server
current_directory = os.path.dirname(os.path.realpath(__file__))

returnCodeLoadDropdown = os.system("pscp "+ sshAddress + dropDownMenuFile + " " + current_directory + "/dropdownEntries.npy")

# load dictionary with entries of the dropdown menus
loadedNumpyFile = np.load( 'dropdownEntries.npy' )
#loadedNumpyFile = np.load( 'dropdownMenu.npy')
datajointDict = loadedNumpyFile.item()
# get current databaseimport datetime
now = datetime.datetime.now()
date = now.strftime('%Y-%m-%d')

class window(wx.Frame):
# Creating the class with the name window and initializing it so that this is the fist thing that opens
# after running the script.
    def __init__(self,parent,id):
        wx.Frame.__init__(self,parent,id,'Data Transfer Tool, Rig',size=(1550,900))
        panel=wx.Panel(self)
        submitButton=wx.Button(panel,label="Submit",pos=(1100,795),size=(160,40))

        quitButton=wx.Button(panel,label="Quit",pos=(1330,795),size=(160,40)) 

# =============================================================================
# SHOW MESSAGE IF TRANSFER OF DROPDOWN FILE WAS NOT SUCCESSFUL
# =============================================================================
        
        if returnCodeLoadDropdown != 0:
            errMessage = "An error (code %s) occured while trying to copy the numpy " % returnCodeLoadDropdown + \
                            "file with the dropdown menu entries from the server to this PC." 
                            
            wx.MessageBox(errMessage, "Error Message" ,wx.OK | wx.ICON_INFORMATION) 
        
# =============================================================================
# MOUSE DETAILS
# =============================================================================
        wx.StaticBox(panel, -1, 'MOUSE DETAILS', (30, 50), size=(1480, 220))

        #Enter the mouse name
        wx.StaticText(panel, pos=(50,100),label="Enter the unique mouse name:")
        mouseNameDict = datajointDict['Mouse']
        self.mouseName = wx.ComboBox(panel, -1, pos=(460,95),size=(160,-1),
                                choices = mouseNameDict, style=wx.CB_READONLY)
        self.mouseName.Bind(wx.EVT_COMBOBOX, self.mouseNameSelectedEvent)

        # Display information about the mouse
        wx.StaticText(panel, pos=(50,150),label="First experiment date (yyyy-mm-dd):")
        self.startDate = wx.StaticText(panel, -1, pos=(460,150),size=(160,-1))

        # Display current day
        wx.StaticText(panel, pos=(50,200),label="Current day of the mouse:")
        self.day = wx.StaticText(panel, -1, pos=(460,200),size=(160,-1))

        # mouse id
        wx.StaticText(panel, pos=(1100,100),label="Mouse ID:")
        self.mouseID = wx.StaticText(panel, -1, pos=(1330,95),size=(160,-1))
        # Enter the date of birth of Mouse
        wx.StaticText(panel, pos=(650,100),label="Date of birth (yyyy-mm-dd):")
        self.dob  = wx.StaticText(panel, -1, pos=(910,100),size=(160,-1))

        # Enter the sex of the mouse
        wx.StaticText(panel, pos=(650,150),label="Sex of the mouse:")
        self.sex = wx.StaticText(panel,-1,pos = (910,150))

        # Last experiment
        wx.StaticText(panel, pos=(650,200),label="Last experiment (yyyy-mm-dd):")
        self.lastExperiment = wx.StaticText(panel,-1,pos = (910,200))

        # Enter the mouse strain
        wx.StaticText(panel, pos=(1100,150),label="Mouse strain:")
        self.strain = wx.StaticText(panel,-1,pos=(1330,150))

## Exp
        wx.StaticBox(panel, -1, 'EXPERIMENT DETAILS', (30, 300), size=(1480, 340))

        # Enter the date of birth of Experiment
        wx.StaticText(panel, pos=(50,350),label="Current date (yyyy-mm-dd):")
        self.doe  = wx.TextCtrl(panel, -1, pos=(460,345),size=(160,-1))
        self.doe.SetValue(date)

        # Enter the name of Experimenter
        wx.StaticText(panel, pos=(650,350),label="Enter name of experimenter:")
        users = datajointDict['Experimenter']
        self.experimenter  = wx.ComboBox(panel, -1, pos=(910,345),size=(160,-1),
                                    choices=users, style = wx.CB_READONLY)
        testSel = self.experimenter.FindString(defaultExperimenter)
        self.experimenter.SetSelection(testSel)

        # Enter the Rig Name
        wx.StaticText(panel, pos=(1100,350),label="Select the Rig-ID:")
        rigIdDict = datajointDict['Rig']
        self.rigId  = wx.ComboBox(panel, -1, pos=(1330,345),size=(160,-1),
                            choices=rigIdDict, style = wx.CB_READONLY)
        item = self.rigId.FindString(defaultRigString)
        self.rigId.SetSelection(item)

        # Enter the number of attempts
        wx.StaticText(panel, pos=(50,400),label="Enter attempt (starts with 1):")
        self.attempt  = wx.TextCtrl(panel, -1, pos=(460,395),size=(160,-1))
        self.attempt.SetValue('1')

        # Enter joystick
        wx.StaticText(panel, pos=(50,450),label="Enter the joystick:")
        joystickDict = datajointDict['Joystick']
        self.joystickType=wx.ComboBox(panel, -1,pos=(460,445), size=(160,-1),
                        choices=joystickDict, style = wx.CB_READONLY)
        item = self.joystickType.FindString(defaultJoystick)
        self.joystickType.SetSelection(item)


        # Enter task
        wx.StaticText(panel, pos=(650,450),label="Enter the Task:")
        task = datajointDict['Task']
        self.taskType=wx.ComboBox(panel, -1,pos=(910,445), size=(160,-1),
                                choices=task, style = wx.CB_READONLY)
        item = self.taskType.FindString(defaultTask)
        self.taskType.SetSelection(item)


        #Enter info about forcefield
        wx.StaticText(panel, pos=(650,400),label="Enter the Forcefield:")
        ff = datajointDict['ForceField']
        self.forceField=wx.ComboBox(panel, -1,pos=(910,395), size=(160,-1),
                                    choices=ff, style = wx.CB_READONLY)
        item = self.forceField.FindString('none')
        self.forceField.SetSelection(item)

        #Enter info about anesthesia
        wx.StaticText(panel, pos=(1100,400),label="Anesthesia:")
        anesthesiaDict = datajointDict['Anesthesia']
        self.anesthesia  = wx.ComboBox(panel, -1, pos=(1330,395),size=(160,-1),
                                    choices=anesthesiaDict, style = wx.CB_READONLY)
        item = self.anesthesia.FindString('awake')
        self.anesthesia.SetSelection(item)

# =============================================================================
# OPTOGENETICS        
# =============================================================================
        
        # optogenetics
        wx.StaticText(panel, pos=(50,500),label="Optogenetics:")
        optogeneticsDict = datajointDict['Optogenetics']
        self.optogenetics=wx.ComboBox(panel, -1,pos=(460,495), size=(160,-1),
                                choices=optogeneticsDict, style = wx.CB_READONLY)
        item = self.optogenetics.FindString('none')
        self.optogenetics.SetSelection(item)

        self.optogenetics.Bind(wx.EVT_COMBOBOX, self.optogeneticsSelectedEvent)
        # Checkbox for new entry
        self.newOptogenetics = wx.CheckBox(panel, -1, pos = (200,500),
                                         label = 'Create new entry')
        self.newOptogenetics.Bind( wx.EVT_CHECKBOX, self.newOptoEvent)

        # Enter Optogenetics Variant
        wx.StaticText(panel, pos=(650,500),label="Optogenetics Variant:")
        optVarDict = datajointDict['OptogeneticsVariant']
        self.optVar  = wx.ComboBox(panel, -1, pos=(910,495),size=(160,-1),
                                choices=optVarDict, style = wx.CB_READONLY)
        item = self.optVar.FindString(defaultOptoVariant)
        self.optVar.SetSelection(item)
        self.optVar.Disable()
        
        # Opto Region
        wx.StaticText(panel, pos=(1100,500),label="Optogenetics Region:")
        optRegDict = datajointDict['OptogeneticsRegion']
        self.optRegion=wx.ComboBox(panel, -1,pos=(1330,495), size=(160,-1),
                                choices=optRegDict, style = wx.CB_READONLY)
        item = self.optRegion.FindString('none')
        self.optRegion.SetSelection(item)
        self.optRegion.Disable()

        # Enter the pulse frequency
        wx.StaticText(panel, pos=(1100,550),label="Pulse Frequency(Hz):")
        self.pulseFreq  = wx.TextCtrl(panel, -1, pos=(1330,545),size=(160,-1))
        self.pulseFreq.SetValue('-1')
        self.pulseFreq.Disable()

        # Enter the laser_power
        wx.StaticText(panel, pos=(50,550),label="Laser Power(mW):")
        self.laserPower  = wx.TextCtrl(panel, -1, pos=(460,545),size=(160,-1))
        self.laserPower.SetValue('-1')
        self.laserPower.Disable()

        # Enter the pulse length
        wx.StaticText(panel, pos=(650,550),label="Pulse Length(ms):")
        self.pulseLength  = wx.TextCtrl(panel, -1, pos=(910,545),size=(160,-1))
        self.pulseLength.SetValue('-1')
        self.pulseLength.Disable()

        # optogenetics timing
        wx.StaticText(panel, pos=(50,600),label="Optogenetics Timing:")
        optTimeDict = datajointDict['OptogeneticsTiming']
        self.optTime=wx.ComboBox(panel, -1,pos=(460,595), size=(160,-1),
                                choices=optTimeDict, style = wx.CB_READONLY)
        item = self.optTime.FindString('none')
        self.optTime.SetSelection(item)
        self.optTime.Disable()
        
        # Enter the deeplabcut config file to use for making predictions  Default is the last model
#        wx.StaticText(panel, pos=(650,600),label="Deeplabcut config file:")
#        config_file = ['/data/deeplabcut_weights/Mackenzie-ReachingMESO-2019-01-21/config.yaml']#datajointDict['model_dict']['model_title']
#        defaultModel = config_file[-1]
#        self.config_to_use  = wx.ComboBox(panel, -1, pos=(910,595),size=(160,-1),
#                                    choices=config_file, style = wx.CB_READONLY)
#        testSel = self.config_to_use.FindString(defaultModel)
#        self.config_to_use.SetSelection(testSel)
#        
#        # Enter the iteration to use. Default is the iteration in the config file
#        wx.StaticText(panel, pos=(1100,600),label="Iteration:")
##        # Read config file
#        iteration = ['/data/deeplabcut_weights/Mackenzie-ReachingMESO-2019-01-21/config.yaml','test']#datajointDict['model_dict']['model_title']
#        defaultiter = iteration[-1]
#        self.iteration_to_use  = wx.ComboBox(panel, -1, pos=(1200,595),size=(160,-1),
#                                    choices=config_file, style = wx.CB_READONLY)
##        self.iter_to_use  = wx.ComboBox(panel, -1, pos=(950,595),size=(160,-1),choices=defaultiter, style = wx.CB_READONLY)
#        testSel = self.iteration_to_use.FindString(defaultiter)
#        self.iteration_to_use.SetSelection(testSel)
# =============================================================================
# DATA TRANSFER
# =============================================================================
        wx.StaticBox(panel, -1, 'DATA TRANSFER', (30, 650), size=(1480, 220))

        # Enter the  Experiment type
        wx.StaticText(panel, pos=(50,700),label="Select the detailed experiment file:")
        self.experimentType=wx.FilePickerCtrl(panel, path="", message="Select the experiment type", wildcard="*",pos=(460,695), size=(160,-1), name="experiment")
        # Enter the path for Joystick data
        wx.StaticText(panel, pos=(650,700),label="Select the joystick data:")
        self.joystick=wx.FilePickerCtrl(panel, path="", message="Select the joystick data", wildcard="*",pos=(910,695), size=(160,-1), name="joystick")
        # Enter the path for Reward data
        wx.StaticText(panel, pos=(1100,700),label="Select the reward data:")
        self.reward=wx.FilePickerCtrl(panel, path="", message="Select the reward data", wildcard="*",pos=(1330,695), size=(160,-1), name="reward")
        # Enter the path for Trial data
        wx.StaticText(panel, pos=(50,750),label="Select the trial data:")
        self.trial=wx.FilePickerCtrl(panel, path="", message="Select the trial data", wildcard="*",pos=(460,745), size=(160,-1), name="trial")
        # Enter the path for video data
        wx.StaticText(panel, pos=(650,750),label="Select the video file(s):")
        self.chooseButton=wx.Button(panel,label="Choose Files",pos=(910,745),size=(160,-1))
        # Enter the path for Reward data
        wx.StaticText(panel, pos=(1100,750),label = "Select the calibration files:")
        self.calibButton = wx.Button(panel,label = "Choose Files", pos=(1330,745),size=(160,-1))
#        self.reward=wx.FilePickerCtrl(panel, path="", message="Select the calibration files", wildcard="*",pos=(1330,745), size=(160,-1), name="calibration")

        # Enter the path for Timing Files
        wx.StaticText(panel, pos=(650,800),label = "Select the timing files:")
        self.timingButton = wx.Button(panel,label = "Choose Files", pos=(910,795),size=(160,-1))


        # Enter comments
        wx.StaticText(panel, pos=(50,800),label="Any comments during the experiment:")
        self.sessionNotes = wx.TextCtrl(panel, -1, pos=(460,795),size=(160,-1))
        self.Bind(wx.EVT_BUTTON,self.chooseFile,self.chooseButton)
        self.Bind(wx.EVT_BUTTON,self.calibFile,self.calibButton)
        self.Bind(wx.EVT_BUTTON,self.timingFile,self.timingButton)
        self.Bind(wx.EVT_BUTTON,self.closebutton,quitButton)
        self.Bind(wx.EVT_CLOSE,self.closewindow)
        self.Bind(wx.EVT_BUTTON,self.submitbutton,submitButton)

        # variable to indicate if file dialog has been chosen
        self.videoFileChoosen = False
        self.calibFileChoosen = False
        self.timingFileChoosen = False
        # variable to remember warning shown
        self.noFileWarningAlreadyShown = False
        
        self.panel = panel
        

    def closewindow(self,event):
        self.Destroy()
    def closebutton(self, event):
        self.Close(True)
        
    def chooseFile(self,event):
        """
        Create and show the Open FileDialog
        """
        self.video= wx.FileDialog( self, "Select the Video Files", "", "", "All files(*.*)|*",
                    style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_PREVIEW)

        if self.video.ShowModal() == wx.ID_OK:
            self.files=self.video.GetPaths()
            self.chooseButton.SetLabel(str(len(self.video.GetPaths()))+" Files chosen")
            self.videoFileChoosen = True
        self.video.Destroy()
     
    def calibFile(self,event):
        """
        Create and show the Open FileDialog
        """
        self.calib= wx.FileDialog( self, "Select the Calibration Files", "", "", "All files(*.*)|*",
                    style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_PREVIEW)

        if self.calib.ShowModal() == wx.ID_OK:
            self.calibFiles=self.calib.GetPaths()
            self.calibButton.SetLabel(str(len(self.calib.GetPaths()))+" Files chosen")
            self.calibFileChoosen = True
        self.calib.Destroy()

    def timingFile(self,event):
        """
        Create and show the Open FileDialog
        """
        self.timing= wx.FileDialog( self, "Select the Timing Files", "", "", "All files(*.*)|*",
                    style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | wx.FD_PREVIEW)

        if self.timing.ShowModal() == wx.ID_OK:
            self.timingFiles=self.timing.GetPaths()
            self.timingButton.SetLabel(str(len(self.timing.GetPaths()))+" Files chosen")
            self.timingFileChoosen = True
        self.timing.Destroy()

    def mouseNameSelectedEvent(self, event):
        """Event handling for selection in mouse dropdown menu"""

        mouseName = self.mouseName.GetValue()
        mouseDict = datajointDict['MouseDict'][mouseName]
        self.startDate.SetLabel( str( mouseDict['startDate']))
        self.mouseID.SetLabel( str( mouseDict['mouse_id']) )
        self.dob.SetLabel( str(mouseDict['dob']) )
        self.sex.SetLabel( mouseDict['sex'])
        self.strain.SetLabel( mouseDict['strain'])
        self.day.SetLabel( str(mouseDict['day']))
        self.lastExperiment.SetLabel( str(mouseDict['lastExperiment']))


    def optogeneticsSelectedEvent(self, event):
        """Event handling if the user selects an option in the Scan Details dropdown menu"""
        
        sel_opto = self.optogenetics.GetValue()
        optoDict = datajointDict['Optogenetics_dict'][sel_opto]

        self.pulseFreq.SetValue( str( optoDict['pulse_frequency'] ))
        self.pulseLength.SetValue( str( optoDict['pulse_length']))
        self.laserPower.SetValue( str( optoDict['laser_power']))
        self.optRegion.SetValue( optoDict['opto_region_name'])
        self.optTime.SetValue( optoDict['opto_timing_name'])
        self.optVar.SetValue( optoDict['opto_variant_name'])
        
        
    def newOptoEvent(self, event):
        """Event handling when clicking the checkbox 'new Optogenetics entry' """

        if self.newOptogenetics.GetValue():
            # checkbox 'new entry' selected
            # Enter the date of Experiment
            self.optogenetics.Hide()
            self.optogenetics  = wx.TextCtrl(self.panel, -1, pos=(460,495),size=(160,-1) )

            # activate the fields to allow entering a new experiment type
            self.optVar.Enable()
            self.optRegion.Enable()
            self.pulseFreq.Enable()
            self.laserPower.Enable()
            self.pulseLength.Enable()
            self.optTime.Enable()
            
        else:
            # checkbox 'new entry' deselected
            self.optogenetics.Hide()
            self.optogenetics=wx.ComboBox(self.panel, -1,pos=(460,495), size=(160,-1),
                                choices=datajointDict['Optogenetics'], style = wx.CB_READONLY)
            item = self.optogenetics.FindString('none')
            self.optogenetics.SetSelection(item)
            self.optogenetics.Bind(wx.EVT_COMBOBOX, self.optogeneticsSelectedEvent)
            
            self.optogeneticsSelectedEvent('Update fields')
            # deactivate the checkboxes
            self.optVar.Disable()
            self.optRegion.Disable()
            self.pulseFreq.Disable()
            self.laserPower.Disable()
            self.pulseLength.Disable()
            self.optTime.Disable()

    def submitbutton(self,event):
        """Event handling when clicking submit button

        Selected files are transfered to the server and a .npy dictionary with
        the values of the dropdown menus and text fields is stored
        """
        # TODO: show progress bar when the upload takes long for big files

        if self.startDate.GetLabel() == 'None':
            # this is the first experiment for this mouse
            start = arrow.get(self.doe.GetValue(),'YYYY-MM-DD')
        else:
            start = arrow.get(self.startDate.GetLabel(),'YYYY-MM-DD')

        current = arrow.get(self.doe.GetValue(),'YYYY-MM-DD')
        ndays = ((current - start).days +1)

        # create file extension for the server
        fileExtension = ("_mouse-"+ self.mouseName.GetValue() +
                         "_day-" + str(ndays) +
                         "_attempt-" + self.attempt.GetValue() +
                         "_doe-" + self.doe.GetValue().replace('-','') +
                         "_rig-" + self.rigId.GetValue() )

        gui_data_path = (savePathForNpy + "rigGui" + fileExtension + ".npy")

        experiment_path = (savePathForData + "experiment/" + "rigExperiment" + fileExtension + ".data")
        joystick_path = (savePathForData + "joystick/" + "rigJoystick" + fileExtension + ".data")
        reward_path = (savePathForData + "reward/" + "rigReward" + fileExtension + ".data")
        trial_path = (savePathForData + "trial/" + "rigTrial" + fileExtension + ".data")
#        calib_path = (savePathForData + "calib/" + "rigTrial" + fileExtension + ".data")

# =============================================================================
#         MATCH VIDEO FILES WITH CORRESPONDING CAMERA_ID AND PART_ID
# =============================================================================
        if self.videoFileChoosen == True:
            video_paths = list()
            camera_id_list = list()
            part_id_list = list()

            file_paths_local = self.files;
            file_paths_local.sort()  # sort to get increasing time stamps (on directories to have same ordering)

            file_names = [os.path.basename(path) for path in self.files]

            saved_camera_id = None

            for file in file_names:
                # get filename
                regex = re.compile(r'VIDEO\d')
                search_result = regex.search(file)
                if search_result == None:
                    raise Exception('File name had wrong format. "VIDEO" followed by number could not be found)')

                camera_id = int( search_result.group()[-1] )  # get video number from file name

                # calculate part_id
                if camera_id != saved_camera_id:
                    # new video processed
                    part_id = 0
                    saved_camera_id = camera_id
                else:
                    # same video, therefore increase part counter
                    part_id += 1

                video_paths.append(savePathForData + "video/" +
                             "rigVideo" + "_mouse-"+ self.mouseName.GetValue() +
                             "_day-" + str(ndays) +
                             "_attempt-" + self.attempt.GetValue() +
                             "_camera-" + str(camera_id) +
                             "_part-" + str(part_id) +
                             "_doe-" + self.doe.GetValue().replace('-','') +
                             "_rig-" + self.rigId.GetValue() + ".avi")

                camera_id_list.append(camera_id)
                part_id_list.append(part_id)
        else:
            # no video file was chosen
            video_paths = None
            camera_id_list = None
            part_id_list = None
            file_paths_local  = None

# =============================================================================
#         MATCH CALIBRATION FILES WITH CORRESPONDING CAMERA_ID 
# =============================================================================
        if self.calibFileChoosen == True:
            calib_paths = list()
#            camera_id_list = list()
#            part_id_list = list()

            calib_file_paths_local = self.calibFiles;
            calib_file_paths_local.sort()  # sort to get increasing time stamps (on directories to have same ordering)

            file_names = [os.path.basename(path) for path in self.calibFiles]

            saved_camera_id = None

            for file in file_names:
                # get filename
                regex = re.compile(r'CALIBRATION\d')
                search_result = regex.search(file)
                if search_result == None:
                    raise Exception('File name had wrong format. "CALIBRATION" followed by number could not be found)')

                camera_id = int( search_result.group()[-1] )  # get calibration number from file name

                # calculate part_id
                if camera_id != saved_camera_id:
                    # new video processed
                    part_id = 0
                    saved_camera_id = camera_id
                else:
                    # same video, therefore increase part counter
                    part_id += 1

                calib_paths.append(savePathForData + "calibration/" +
                             "rigCalibration" + "_mouse-"+ self.mouseName.GetValue() +
                             "_day-" + str(ndays) +
                             "_attempt-" + self.attempt.GetValue() +
                             "_camera-" + str(camera_id) +
                             "_part-" + str(part_id) +
                             "_doe-" + self.doe.GetValue().replace('-','') +
                             "_rig-" + self.rigId.GetValue() + ".jpg")

#                camera_id_list.append(camera_id)
#                part_id_list.append(part_id)
        else:
            # no video file was chosen
            calib_paths = None
#            camera_id_list = None
#            part_id_list = None
            calib_file_paths_local  = None
            
# =============================================================================
#         MATCH CALIBRATION FILES WITH CORRESPONDING CAMERA_ID 
# =============================================================================
        if self.timingFileChoosen == True:
            timing_paths = list()
            timing_file_paths_local = self.timingFiles;
            timing_file_paths_local.sort()  # sort to get increasing time stamps (on directories to have same ordering)

            file_names = [os.path.basename(path) for path in self.timingFiles]
            
            saved_camera_id = None

            for file in file_names:
                # get filename
                if 'LABVIEW' in file:
                    filetype = 'LABVIEW'
                elif 'VIDEO1' in file:
                    filetype = 'camera-1'
                else:
                    filetype = 'camera-2'
                    
#                regex = re.compile(r'CALIBRATION\d')
#                search_result = regex.search(file)
#                if search_result == None:
#                    raise Exception('File name had wrong format. "CALIBRATION" followed by number could not be found)')
#
#                camera_id = int( search_result.group()[-1] )  # get calibration number from file name
#
#                # calculate part_id
#                if camera_id != saved_camera_id:
#                    # new video processed
#                    part_id = 0
#                    saved_camera_id = camera_id
#                else:
#                    # same video, therefore increase part counter
#                    part_id += 1

                timing_paths.append(savePathForData + "timingFiles/" +
                             "sync_file-" + filetype +
                             "_mouse-"+ self.mouseName.GetValue() +
                             "_day-" + str(ndays) +
                             "_attempt-" + self.attempt.GetValue() +
                             "_doe-" + self.doe.GetValue().replace('-','') +
                             "_rig-" + self.rigId.GetValue() + ".npy")
        else:
            # no video file was chosen
            timing_paths = None
            timing_file_paths_local  = None         
            
            
# =============================================================================
#       CHECK IF ALL FILES IN DATA TRANSFER ARE SELECTED
# =============================================================================

        missing = ''

        if len(self.experimentType.GetPath()) == 0:
            missing += '- Detailed experiment file\n'
            experiment_path = 'None'
            
        if len(self.joystick.GetPath()) == 0:
            missing += '- Joystick data\n'
            joystick_path = 'None'
            
        if len(self.reward.GetPath()) == 0:
            missing += '- Reward data\n'
            reward_path = 'None'
            
        if len(self.trial.GetPath()) == 0:
            missing += '- Trial data\n'
            trial_path = 'None'
            
        if video_paths == None:
            missing += '- Video files\n'
            
        if timing_paths == None:
            missing += '- Timing Files\n'
            
        if len(missing) != 0:
            if self.noFileWarningAlreadyShown == False:
                # display warning to user and abort upload if first time
                message = 'Warning! The following files have not been selected for upload:\n' + missing + '\n'\
                          'No data has been sent to the server. If you do not want to upload these files, ' + \
                          'click submit again. This message will only appear once.'
                wx.MessageBox(message, "Missing files" ,wx.OK | wx.ICON_INFORMATION) 
                self.noFileWarningAlreadyShown = True
                return


# =============================================================================
# CHECK IF NEW ENTRY OPTOGENETICS ENTRY  
# =============================================================================
                
        # check if new scanDetails checkbox is active, if the entered name is unique
        if self.newOptogenetics.GetValue():
            # checkbox 'new entry' selected
            if self.optogenetics.GetValue() in datajointDict['Optogenetics']:
                message = 'The entry in Optogenetics is already in the database! No data was transfered to the server.\n' + \
                    'Choose a different name for the optogenetics key (EXPERIMENT DETAILS, 1st column, 4th row) ' + \
                    'or uncheck the checkbox "Create new entry"'
                wx.MessageBox(message, "Primary key already in database" ,wx.OK | wx.ICON_INFORMATION)
                return
            if self.optogenetics.GetValue() == "":
                message = 'The optogenetics key (EXPERIMENT DETAILS, 1st column, 4th row) is empty.\n' + \
                    'This is not allowed!'
                wx.MessageBox(message, "Empty primary key" ,wx.OK | wx.ICON_INFORMATION)
                return
            
# =============================================================================
#       CREATE NPY DICT
# =============================================================================

        data = { # primary keys for session
                'mouse_name':self.mouseName.GetValue(),
                'day': ndays,
                'attempt': self.attempt.GetValue(),
                # additional session information
                'doe':self.doe.GetValue(),
                'rig_id': int(self.rigId.GetValue() ),
                'experimenter':self.experimenter.GetValue(),
                'anesthesia':self.anesthesia.GetValue(),
                'task':self.taskType.GetValue(),
                'forcefield':self.forceField.GetValue(),
                'joystick':self.joystickType.GetValue(),
                'session_notes':self.sessionNotes.GetValue(),
                
                # opotgenetics
                'opto_name': self.optogenetics.GetValue(),
                
                #if new entry, the following fields are needed:
                'new_optogenetics_entry':self.newOptogenetics.GetValue(),
                'opto_variant_name':self.optVar.GetValue(),
                'opto_timing_name':self.optTime.GetValue(),
                'opto_region_name':self.optRegion.GetValue(),
                'pulse_frequency': float(self.pulseFreq.GetValue()),
                'laser_power': float(self.laserPower.GetValue()),
                'pulse_length': float(self.pulseLength.GetValue()),

                # file paths on server (local files that are uploaded)
                'experiment_path': experiment_path,
                'joystick_path':joystick_path,
                'reward_path':reward_path,
                'trial_path':trial_path,
                'video_paths':video_paths,
                'calibration_paths' : calib_paths,
                # video_id list to match paths with corresponding ids
                'camera_id_list':camera_id_list,
                'part_id_list':part_id_list,

                # source file paths (local files that are uploaded)
                'source_experiment_path':self.experimentType.GetPath(),
                'source_joystick_path':self.joystick.GetPath(),
                'source_reward_path':self.joystick.GetPath(),
                'source_trial_path':self.reward.GetPath(),
                'source_video_paths':file_paths_local,
                'source_calib_paths':calib_file_paths_local,
                'source_timing_paths':timing_file_paths_local,

                #
                'timing_paths': timing_paths,
                # maybe useful information
                'time_stamp' : datetime.datetime.now()
                }
        localNumpyFile = os.path.join( current_directory, 'tmp_numpy', 'localNpyRig' + fileExtension + '.npy' )
        np.save( localNumpyFile, data )

      
# =============================================================================
#       TRANSFER FILES
# =============================================================================

        print('Starting data file transfer...')
        ## TODO show process of the upload in the GUI window
        
        # transfer raw data to the server
        codes = dict()
        if len(self.experimentType.GetPath()) != 0:
            codes['experimentDetails'] = os.system('pscp "'+self.experimentType.GetPath()+ '" ' + sshAddress + experiment_path)
        if len(self.joystick.GetPath()) != 0:
            codes['joystick'] = os.system('pscp "'+self.joystick.GetPath()+ '" ' + sshAddress + joystick_path)
        if len(self.reward.GetPath()) != 0:
            codes['reward'] = os.system('pscp "'+self.reward.GetPath()+ '" ' + sshAddress + reward_path)
        if len(self.trial.GetPath()) != 0:
            codes['trial'] = os.system('pscp "'+self.trial.GetPath()+ '" ' + sshAddress + trial_path)

        if self.videoFileChoosen == True:
            for index, videoPath in enumerate(file_paths_local):
                # " " around videoPath to avoid error when using file names with spaces
                codes['video%s'%index] = os.system('pscp "' + videoPath + '" ' + sshAddress + video_paths[index])
        
        if self.calibFileChoosen == True:
            for calibIndex, calibPath in enumerate(calib_file_paths_local):
                codes['calib%s'%calibIndex] = os.system('pscp "' + calibPath + '" ' + sshAddress + calib_paths[calibIndex])
        
        if self.timingFileChoosen == True:
            for timingIndex, timingPath in enumerate(timing_file_paths_local):
                codes['timing%s'%timingIndex] = os.system('pscp "' + timingPath + '" ' + sshAddress + timing_paths[timingIndex])
#                codes['calib%s'%calibIndex] = os.system('pscp "' + calibPath + '" ' + sshAddress + calib_paths[calibIndex]
        # transfer numpy file to tmp directory
        codes['npy'] = os.system("pscp " + localNumpyFile + " " + sshAddress + gui_data_path)

# =============================================================================
#       DISPLAY SUCCESS OR ERROR MESSAGE     
# =============================================================================
        
        # check return codes 
        if all( [returnCode==0 for returnCode in codes.values()] ): 
            # all return codes 0 => all uploads were successful
            title = 'Success'
            message = "All data transferred successfully. In total %s files were transfered" % len(codes)
                      
        elif all( [returnCode!=0 for returnCode in codes.values()] ):
            # all uploads failed
            title = 'Error: No files transferred'
            message = 'All uploads to the server failed. Check the connection to the server (e.g. ssh setup) ' + \
                    'and try again.'
        else:
            # only some uploads failed
            title = 'Seriour Error!'
            message = "Only some uploads failed! Attempted to upload %s files.\n" % len(codes) + \
                    "Return codes of the individual uploads:\n%s" % codes + '\n\n' + \
                    "Manually check which files were uploaded and delete transfered files on the server to " + \
                    "avoid invalid file links!!"
            
        wx.MessageBox(message, title ,wx.OK | wx.ICON_INFORMATION)
        print(title)
        print(message)
        
        # reset variable to remember warning shown in case multiple sessions are uploaded
        self.noFileWarningAlreadyShown = False
        
if __name__ == '__main__':
    app=wx.App()
    frame=window(parent=None,id=-1)
    frame.Show()
    app.MainLoop()
