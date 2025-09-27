## Dynamics of vk user registration in pro-war groups

Several pro-war VK groups were analyzed. Registration dates of their members were collected, and war-related anomalies in the dates distribution wwere explored.

The results can be found in `results/user_reg_dynamics`.

The workflow can be reproduced by running `user_reg_dynamics.ipynb` in Google Colab. By default, it uses pre-loaded data and doesn't require VK access. The code for re-loading the data from VK is still pressent, but it is likely that API changed since the last run (and an API key is required anyway).



## Detection of group members with z-avatars

### 1. Load information about group members via VK API

***load_group_members_from_vk.py***

Group to work with is set by: *GROUP_ID* <br>
Output: *"<GROUP_ID>_members.pkl"*
  
### 2. Load avatars of group members

***load_avatars_from_vk.py***

The result of the previous step is set by: *FPATH_USERS_INFO* <br>
Number of users, for which avatars should be loaded: *N_AVATARS_TO_LOAD*

A random subset of *N_AVATARS_TO_LOAD* members is taken from all group members having an avatar.

The script will create a folder with the avatar pictures. <br>
It will also create *users.pkl* file with the information about the subset of members.
  
### 3. Zip the folder with avatars and upload it to Google Drive

### 4. Run zdetector_rand_avatars.ipynb in Google Colab

- Open ***zdetector_rand_avatars.ipynb*** in Colab
- Set *data_name* and provide a path to the archive with avatars on the Google Drive via *data_url*
- Run the cells, one by one
- In the middle of the notebook, a csv-file with the classification results will be downloaded to your local drive (a dialog windo will open, and you will have to provide a pathwhere to download)
- In the end of the notebook, two zip-archives will be downloaded: with the avatars containing Z, and with avatars containing russian tricolor.

### 5. Unzip the archive with Z-avatars

### 6. Manually remove false positives

Go to the unzipped folder and manually remove all avatars that do not contain Z. <br>
There will be a lot of them, since a very low detection threshold is used (not to miss too many avatars).

### 7. Visualize the result

***calc_avatar_time_distr.py***

*FPATH_USERS_INFO* - path to the file with information on the subset of members (*users.pkl*, see Step 2) <br>
*FPATHS_Z* - 1-element list containing a path to the folder with the Z-avatars (see Step 6) <br>
*GROUP_NAME* - legend to put onto plots

The script will produce three figures:
- Temporal distribution of the number of the group members who have an avatar
- Temporal distribution of the number of the group members who have a Z-avatar
- Temporal distribution of the percentage of the group members who have a Z-avatar (ratio of the previous two distributions)

The last plot is temporally smoothed, for better presentation.

You can leave the figures opened, and re-run this script for another group - new results will be visualized together with the old ones.





  