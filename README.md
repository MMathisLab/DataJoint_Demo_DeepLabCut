# dj-mathis-sharing

- TOC:

- We use the 2P pipeline from here (i.e., mice, meso), and that serves as the basis for other schemas for us: https://github.com/cajal/pipeline

    - https://github.com/cajal/pipeline/tree/master/python/pipeline


- `dlc.py` is our schema for automating 2d and 3d keypoint extraction based on a DLC project. Works for any DLC project created in the 2.x framework, excluding multi-animals (currently). This should work without modifications, except to path for where the video data is, etc.

- `transfer...py` is the GUI that you can put on each rig that collects data for DJ insertion! Of course modify to fit your needs. You will need to have wxPython installed on the computer this is hosted on.

- `createdropdown..py` fetches information in the database on a given mouse, so you can automatically populate the transfer GUI. Of course modify to fit your needs.

- `populate_dlc.py` can be run at any time to automatically populate the dlc schema, both 2D and 3D tables.

- `cronjobs` (crontab.sh being the "master") are files to automate when populate_dlc,py, etc runs, you can set to your preferred times with the cron daemon https://phoenixnap.com/kb/set-up-cron-job-linux


