# -*- coding: utf-8 -*-

import os
import pickle
import requests

from tqdm import tqdm

from vk_utils import VkAPI


DIRPATH_BASE = r'D:\WORK\zresult'
avatar_types = ['z']

#GROUP_NAME = 'putin_z'
#GROUP_NAME = 'random_1e6'
GROUP_NAME = 'random_around_24Feb'


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

# Load users' info from disk (for which avatars were previously loaded)
dirpath_group = os.path.join(DIRPATH_BASE, GROUP_NAME)
fpath_users = os.path.join(dirpath_group, 'users.pkl')
with open(fpath_users, 'rb') as fid:
    users = pickle.load(fid)

for av_type in avatar_types:
    
    # Get idx of users with avatars of the given type
    dirname_av_old = f'{GROUP_NAME}_{av_type}'
    dirpath_av_old = os.path.join(dirpath_group, 'avatars', dirname_av_old)
    fnames = os.listdir(dirpath_av_old)
    user_idx = []
    for fname in fnames:
        user_id, _ = os.path.splitext(fname)
        user_idx.append(int(user_id))
        
    # Create folder for reloaded avatars
    dirname_av_new = f'{GROUP_NAME}_{av_type}_new'
    dirpath_av_new = os.path.join(dirpath_group, 'avatars', dirname_av_new)
    if not os.path.exists(dirpath_av_new):
        os.mkdir(dirpath_av_new)
        
    # Reload avatars from vk
    for user_id in tqdm(user_idx):
        user = users[user_id]
        fname_out = str(user_id) + '.jpg'
        fpath_out = os.path.join(dirpath_av_new, fname_out)
        if os.path.exists(fpath_out):
            continue
        url = user['photo_200_orig']
        if url == r'https://vk.com/images/camera_200.png':  # empty avatar
            print('Skip')
            continue
        load_img(url, fpath_out)



