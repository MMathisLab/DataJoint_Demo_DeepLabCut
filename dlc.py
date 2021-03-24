"""
DataJoint Schema for DeepLabCut 2.x
Mathis Lab 2019-2021
mackenzie.mathis@epfl.ch
Supports 2D and 3D DLC via triangulation.
"""

# imports
import datajoint as dj
import os
from pathlib import Path
import shutil
import pandas as pd
import numpy as np
from . import exp

# set constant file paths (edit to where you want data to go):
save_dlc_path = Path('/data/processeddata/deeplabcut2.0_analysed')
schema = dj.schema('dlc', locals(), create_tables=True)

@schema
class DLCModel(dj.Manual):
    definition = """   # Keeps the model title to use for prediction
    -> exp.RawVideo
    config_path  : varchar(1024) # path of configuration file (must be in deeplabcut_weights folder)
    iteration    : int           # iteration number
    shuffle      : int           # shuffle number to use (usually 1)
    trainingindex: int           # index of the Training fraction to use
    scorer       : varchar(512)  # scorer/network name for a particular shuffle, training fraction etc.
    pcutoff      : float         # specifies threshold of the likelihood
    """

@schema
class DeepLabCut(dj.Computed):
   definition=""" # uses DeepLabCut to extract the position of the bodyparts.
   -> DLCModel
   version               : varchar(8) # keeps the deeplabcut version
   joint_name            : varchar(512) # Name of the joints
   ---
   x_pos                 : longblob
   y_pos                 : longblob
   likelihood            : longblob
   time                  : longblob     # time in session for each frame
   """

   def _make_tuples(self, key):

       import deeplabcut
       import deeplabcut.utils.auxiliaryfunctions as dlc_aux

       video_path = (exp.RawVideo() & key).fetch1('video_path')
       video_path = Path(video_path)
       cfg = dlc_aux.read_config(key['config_path'])
       #cfg['iteration'] = key['iteration']
       cfg_tmp = key['config_path'].replace('.yaml', '_tmp.yaml')
       dlc_aux.write_config(cfg_tmp, cfg)
       model = dlc_aux.GetScorerName(cfg, key['shuffle'], cfg['TrainingFraction'][0])

       # analyze video
       dlc_output_h5 = video_path.parent / Path(str(video_path.stem) + model + '.h5')
       dj_output_h5 = os.path.join(str(save_dlc_path),str(str(video_path.stem)+ model + '.h5'))
       dlc_output_pickle = dlc_output_h5.parent / Path(str(dlc_output_h5.stem) + 'includingmetadata.pickle')
       if not os.path.isfile(dj_output_h5):
           deeplabcut.analyze_videos(cfg_tmp, [str(video_path)])
           if os.path.isfile(dlc_output_h5):
               shutil.move(dlc_output_h5, dj_output_h5)
           if os.path.isfile(dlc_output_pickle):
               os.remove(dlc_output_pickle)
           if os.path.isfile(cfg_tmp):
               os.remove(cfg_tmp)

       df = pd.read_hdf(dj_output_h5,'df_with_missing')
       bodyParts = df.columns.get_level_values(1)
       _,idx  = np.unique(bodyParts,return_index=True)
       bodyParts = bodyParts[np.sort(idx)]
       frame_times = np.load((exp.RawVideo()&key).fetch1('camera_timestamps_path'))
       tuple_ = key.copy()
       tuple_['version'] = deeplabcut.__version__
       tuple_['time'] = frame_times
       for bp in bodyParts:
           tuple_['joint_name'] = bp
           tuple_['x_pos'] = df[model][bp]['x'].values
           tuple_['y_pos'] = df[model][bp]['y'].values
           tuple_['likelihood'] = df[model][bp]['likelihood'].values
           self.insert1(tuple_)

       print("\n")
       print("Populated DeepLabCut data from:")
       print("mouse = %s // day = %d // attempt = %d // video = %s" % (key['mouse_name'], key['day'], key['attempt'], key['camera_id']))
       print("\n")
     
   def get2dJointsTrajectory(self,joint_name=[None]):
       """
       Returns a dataframe of x, y coordinates and likelihood of the specified joint_name for a camera_id
       e.g. df = (dlc.DeepLabCut() & "mouse_name= 'Xerus'" & 'day=2' & 'attempt=1' & "camera_id = 1").get2dJointsTrajectory('backhand')
       Input:
           self: A query that relates to one mouse, else error is thrown. Use primary keys to choose the right scorer or version etc.
           camera_id: The camera index as an integer 1 or 2. 1 is side camera and 2 is front camera
           joint_name: Name of the joint as a list or None in case to fetch for all the joint names.
       Output:
           df: A multi index dataframe with scorer names, bodyparts and coordinates of each joint name. This dataframe is similar to the output of DLC dataframe.
       """
       scorer = np.unique(self.fetch('scorer'))[0]
       if joint_name==None:
           bodyparts = self.fetch('joint_name')
       else:
           bodyparts=list(joint_name)
       dataFrame = None
       for bodypart in bodyparts:
           x_pos = (self & ("joint_name='%s'"%bodypart)).fetch1('x_pos')
           y_pos = (self & ("joint_name='%s'"%bodypart)).fetch1('y_pos')
           likelihood = (self & ("joint_name='%s'"%bodypart)).fetch1('likelihood')
           a = np.vstack((x_pos,y_pos,likelihood))
           a = a.T
           pdindex = pd.MultiIndex.from_product([[scorer], [bodypart], ['x', 'y','likelihood']], names=['scorer', 'bodyparts', 'coords'])
           frame = pd.DataFrame(a, columns = pdindex,index = range(0,a.shape[0]))
           dataFrame = pd.concat([dataFrame,frame],axis=1)
       return(dataFrame)

@schema
class DLC3DModel(dj.Manual):
     definition=""" # Keeps the model information to use for 3D deeplabcut pose estimation

     -> exp.Session
     config_path          : varchar(1024) # path of 3d project configuration file (must be in deeplabcut_weights folder)
     scorer               : varchar(512) # scorer/network name for 3d project.
     pcutoff              : float # specifies threshold of the likelihood
     """
#shuffle              : longblob # shuffle numbers to use for each camera(usually 1). Pass as list e.g.[1,1]
#trainingindex        : longblob # index of the Training fraction to use for each camera(usually 0). Pass as list e.g.[0,0]


## shuffle numbers to use for each camera(usually 1). Pass as list e.g.[1,1]
## index of the Training fraction to use for each camera(usually 0). Pass as list e.g.[0,0]
@schema
class DeepLabCut3D(dj.Computed):
     definition=""" # uses DeepLabCut to extract the 3D position of the bodyparts.
     -> DLC3DModel
     version               : varchar(8) # keeps the deeplabcut version
     joint_name            : varchar(512) # Name of the joints
     ---
     x_pos                 : longblob
     y_pos                 : longblob
     z_pos                 : longblob
     """
     def _make_tuples(self, key):

       import deeplabcut
       import glob

       videos = (exp.RawVideo() & key).fetch('video_path')
       cfg3d = key['config_path']
       model = key['scorer']
       try:
          deeplabcut.triangulate(cfg3d, [videos],destfolder = save_dlc_path)
          string_to_search = str('*mouse-'+key['mouse_name']+'_day-'+str(key['day'])+'_attempt-'+str(key['attempt'])+'*'+key['scorer']+'.h5')
          dj_output_h5_filename = glob.glob(os.path.join(save_dlc_path,string_to_search))[0]
          df = pd.read_hdf(dj_output_h5_filename,'df_with_missing')
          bodyParts = df.columns.get_level_values(1)
          _,idx  = np.unique(bodyParts,return_index=True)
          bodyParts = bodyParts[np.sort(idx)]
          tuple_ = key.copy()
          tuple_['version'] = deeplabcut.__version__
          for bp in bodyParts:
               tuple_['joint_name'] = bp
               tuple_['x_pos'] = df[model][bp]['x'].values
               tuple_['y_pos'] = df[model][bp]['y'].values
               tuple_['z_pos'] = df[model][bp]['z'].values
               self.insert1(tuple_)

          print("\n")
          print("Populated 3D data from:")
          print("mouse = %s // day = %d // attempt = %d" % (key['mouse_name'], key['day'], key['attempt']))
          print("\n")
       except:
          print("No videos found for mouse %s day %s and attempt %s "%(key['mouse_name'],str(key['day']),str(key['attempt'])))
    
     def get3dJointsTrajectory(self,joint_name=[None]):
        """
        Returns a dataframe of x, y and z coordinates of the specified joint_name
        e.g. df = (dlc.DeepLabCut3D() & "mouse_name= 'Xerus'" & 'day=2' & 'attempt=1').get3dJointsTrajectory(None)
        Input:
           self: A query that relates to one mouse, else error is thrown. Use primary keys to choose the right scorer or version etc.
           joint_name: Name of the joint as a list or None in case to fetch for all the joint names.
        Output:
           df: A multi index dataframe with scorer names, bodyparts and coordinates of each joint name. This dataframe is similar to the output of DLC dataframe.
        """
        scorer = np.unique(self.fetch('scorer'))[0]
        if joint_name[0]==None:
            bodyparts = self.fetch('joint_name')
        else:
            bodyparts=list(joint_name)
        
        dataFrame = None
        for bodypart in bodyparts:
            x_pos = (self & ("joint_name='%s'"%bodypart)).fetch1('x_pos')
            y_pos = (self & ("joint_name='%s'"%bodypart)).fetch1('y_pos')
            z_pos = (self & ("joint_name='%s'"%bodypart)).fetch1('z_pos')
            a = np.vstack((x_pos,y_pos,z_pos))
            a = a.T
            pdindex = pd.MultiIndex.from_product([[scorer], [bodypart], ['x', 'y','z']], names=['scorer', 'bodyparts', 'coords'])
            frame = pd.DataFrame(a, columns = pdindex,index = range(0,a.shape[0]))
            dataFrame = pd.concat([dataFrame,frame],axis=1)
        return(dataFrame)
