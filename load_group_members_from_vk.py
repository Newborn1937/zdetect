# -*- coding: utf-8 -*-

import os
import pickle

#from tqdm import tqdm

import vk_utils


GROUP_ID = 'putin_z'

FIELDS_TO_LOAD = ['photo_200_orig', 'last_seen', 'status', 'bdate',
                  'has_photo', 'followers_count', 'education']

DIRPATH_OUT = r'D:\WORK\zresult\members_info'


# Initialize VK API
vk = vk_utils.VkAPI()

# Load members' info from VK
members = vk.load_group_members(GROUP_ID, ntoload='all', offset=0,
                                sort_type='id_desc', fields=FIELDS_TO_LOAD)
  
# Save the result
fname_out = f'{GROUP_ID}_members.pkl'
fpath_out = os.path.join(DIRPATH_OUT, fname_out)
with open(fpath_out, 'wb') as fid:
    pickle.dump(members, fid)

