# script to make sure the scripts are called in the right order
bash /data/datajoint/cronjobs/updateDatajoint.sh

bash /data/datajoint/cronjobs/populate_dlc.sh

bash /data/datajoint/cronjobs/populate_behavior.sh

bash /data/datajoint/cronjobs/populate_meso.sh

bash /data/datajoint/cronjobs/populate_elephant.sh
