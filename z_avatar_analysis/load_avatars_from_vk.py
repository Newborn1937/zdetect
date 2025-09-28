# -*- coding: utf-8 -*-

import os
import pickle
import random
import requests

from tqdm import tqdm

from vk_utils import VkAPI


FPATH_USERS_INFO = r'D:\WORK\zresult\members_info\zogolovok_members.pkl'

N_AVATARS_TO_LOAD = 45000

DIRPATH_OUT = r'D:\WORK\zresult\zogolovok'


# Download an image from url
def load_img(url, fpath_out):
    while True:
        try:
            with open(fpath_out, 'wb') as f:
                f.write(requests.get(url).content)
            break
        except Exception as e:
            print(e)


vk_api = VkAPI()

# Create output folders
if not os.path.exists(DIRPATH_OUT):
    os.mkdir(DIRPATH_OUT)
dirpath_avatars = os.path.join(DIRPATH_OUT, 'avatars')
if not os.path.exists(dirpath_avatars):
    os.mkdir(dirpath_avatars)

# Load users' info from disk (which was previously loaded from vk)
with open(FPATH_USERS_INFO, 'rb') as fid:
    users = pickle.load(fid)

if type(users) is list:
    users = {user['id']: user for user in users}

# Get non-deleted users with avatars    
users_active = {user_id: user for user_id, user in users.items()
               if 'deactivated' not in user}
users_with_photo = {user_id: user
                    for user_id, user in users_active.items()
                    if user['has_photo'] == True}

#users_selected = users_with_photo

# Select a random subset of users
user_idx = list(users_with_photo.keys())
random.shuffle(user_idx)
N = min(N_AVATARS_TO_LOAD, len(user_idx))
user_idx = user_idx[:N]
users_selected = {user_id: users_with_photo[user_id] for user_id in user_idx}

# Save the subset of users
fpath_users_sel = os.path.join(DIRPATH_OUT, 'users.pkl')
with open(fpath_users_sel, 'wb') as fid:
    pickle.dump(users_selected, fid)

# Load avatars from VK
for user in tqdm(users_selected.values()):
    fname_out = str(user['id']) + '.jpg'
    fpath_out = os.path.join(dirpath_avatars, fname_out)
    if os.path.exists(fpath_out):
        continue
    url = user['photo_200_orig']
    if url == r'https://vk.com/images/camera_200.png':  # empty avatar
        print('Skip')
        continue
    load_img(url, fpath_out)



