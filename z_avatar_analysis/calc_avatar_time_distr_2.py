# -*- coding: utf-8 -*-


import os
import pickle

import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from vk_utils import VkAPI, get_user_reg_date


#### Settings

#FPATH_USERS_INFO = r'D:\WORK\zresult\putin_z\users.pkl'
FPATH_USERS_INFO = r'D:\WORK\zresult\members_info\putin_z_members.pkl'
FPATHS_AVATARS = [r'D:\WORK\zresult\putin_z\avatars\putin_z_all']
FPATHS_Z = [r'D:\WORK\zresult\putin_z\avatars\putin_z_z']
GROUP_NAME = 'putin_z'

# =============================================================================
# FPATH_USERS_INFO = r'D:\WORK\zresult\random_around_24Feb\users.pkl'
# FPATHS_AVATARS = [r'D:\WORK\zresult\random_around_24Feb\avatars\random_around_24Feb_all']
# FPATHS_Z = [r'D:\WORK\zresult\random_around_24Feb\avatars\random_around_24Feb_z']
# GROUP_NAME = 'random'
# =============================================================================

# =============================================================================
# FPATH_USERS_INFO = r'D:\WORK\zresult\random_1e6\users.pkl'
# FPATHS_AVATARS = [r'D:\WORK\zresult\random_1e6\avatars\random_1e6_all']
# FPATHS_Z = [r'D:\WORK\zresult\random_1e6\avatars\random_1e6_z']
# GROUP_NAME = 'random_all'
# =============================================================================


USER_ID_RANGE = (6.82e8, 7.33e8)


#### Load users' info from disk

with open(FPATH_USERS_INFO, 'rb') as fid:
    users = pickle.load(fid)
    
if isinstance(users, list):
    users = {user['id']: user for user in users}  
    
    
#### Categorize the users 

# All sampled users  
user_idx = list(users.keys())
user_idx = np.array(user_idx)

# Take subset of users
time_mask = (user_idx > USER_ID_RANGE[0]) & (user_idx < USER_ID_RANGE[1])
#user_idx = user_idx[time_mask]

# Active / inactive users
user_idx_active = [user_id for user_id in user_idx
                   if 'deactivated' not in users[user_id]]
user_idx_active = np.array(user_idx_active)

# =============================================================================
# # Look at the users below max. active user id only
# user_id_act_max = np.max(user_idx_active)
# user_idx = user_idx[user_idx <= user_id_act_max]
# user_idx_active = user_idx_active[user_idx_active <= user_id_act_max]
# =============================================================================

# Users who have avatars
user_idx_photo = [user_id for user_id in user_idx_active
                  if users[user_id]['has_photo'] == True]
user_idx_photo = np.array(user_idx_photo)

# Users with information about 'last seen' date
user_idx_last_seen = [user_id for user_id in user_idx_active
                      if 'last_seen' in users[user_id].keys()]
user_idx_last_seen = np.array(user_idx_last_seen)

# Dates at which users were last seen
last_seen_vec = {
        user_id: datetime.datetime.fromtimestamp(users[user_id]['last_seen']['time'])
        for user_id in user_idx_last_seen
        }

# Users who were last seen after the beginning of the war
war_start_date = datetime.datetime.strptime('24-02-2022', '%d-%m-%Y').date()
user_idx_seen_during_war = [user_id for user_id in user_idx_last_seen
                            if last_seen_vec[user_id].date() >= war_start_date]
user_idx_seen_during_war = np.array(user_idx_seen_during_war)

# Users with avatars, who were last seen after the beginning of the war
user_idx_photo_seen_during_war = [
        user_id for user_id in user_idx_last_seen
        if users[user_id]['has_photo'] == True
        and last_seen_vec[user_id].date() >= war_start_date]
user_idx_photo_seen_during_war = np.array(user_idx_photo_seen_during_war)

# Get indices of users from img filenames
files = []
for fpath in FPATHS_AVATARS:
    files += os.listdir(fpath)
user_idx_photo_2 = np.array([int(fname[:-4]) for fname in files])


# Take subset of users
time_mask = (user_idx_photo_2 > USER_ID_RANGE[0]) & (user_idx_photo_2 < USER_ID_RANGE[1])
#user_idx_photo_2 = user_idx_photo_2[time_mask]

# Count users
Nsampled = len(user_idx)
Nactive = len(user_idx_active)
Nphoto = len(user_idx_photo)
Nphoto_2 = len(user_idx_photo_2)

# Print summary
print(f'Total: {Nsampled}')
print(f'Active: {Nactive}, {Nactive / Nsampled}')
print(f'With photo: {Nphoto}, {Nphoto / Nactive}')
print(f'With photo (img): {Nphoto_2}')


#### Find users with z-avatars

# Get indices of z-users from img filenames
files = []
for fpath in FPATHS_Z:
    files += os.listdir(fpath)
user_idx_z = np.array([int(fname[:-4]) for fname in files])

# Z-users who was seen during the war
user_idx_z_seen_during_war = [user_id for user_id in user_idx_z
                              if user_id in user_idx_photo_seen_during_war]
user_idx_z_seen_during_war = np.array(user_idx_z_seen_during_war)

# Check that all z-users were active during the war
for user_id in user_idx_z:
    if ((user_id in user_idx_last_seen) and
        (user_id not in user_idx_seen_during_war)):
        last_seen = last_seen_vec[user_id]
        print(f'Z-user {user_id} was last seen {last_seen}')


#### Calculate histograms

# Histograms: all, active
nbins = 50
h_all, hbins = np.histogram(user_idx, nbins)
h_active, _ = np.histogram(user_idx_active, hbins)
h_all_norm = h_all / np.sum(h_all)
h_active_norm = h_active / np.sum(h_active)
perc_active = h_active / h_all

# Histogram and percentage of users having avatars
h_photo, _ = np.histogram(user_idx_photo, hbins)
h_photo_2, _ = np.histogram(user_idx_photo_2, hbins)
perc_photo_all = h_photo / h_all
perc_photo_act = h_photo / h_active

# Histogram and percentage of users seen during the war
h_last_seen, _ = np.histogram(user_idx_last_seen, hbins)
h_war, _ = np.histogram(user_idx_seen_during_war, hbins)
h_war_photo, _ = np.histogram(user_idx_photo_seen_during_war, hbins)
perc_lastseen_act = h_last_seen / h_active
perc_warphoto_photo = h_war_photo / h_photo

# Histogram of z-users
h_z, _ = np.histogram(user_idx_z, hbins)
h_war_z, _ = np.histogram(user_idx_z_seen_during_war, hbins)
perc_z_photo = h_z / h_photo_2
#perc_warz_warphoto = h_war_z / h_war_photo


#### Convert histogram bins from user idx to dates

# User ID -> Registration date
hbins_t = np.array([get_user_reg_date(user_id) for user_id in hbins])

# Fill None's
hbins_tfix = hbins_t.copy()
for n in range(1, len(hbins_t) - 1):
    if hbins_t[n] is None:        
        tvec_L = np.flip(hbins_t[:n])
        tvec_R = hbins_t[(n + 1):]        
        kL = np.argwhere(tvec_L != None)[0][0]
        kR = np.argwhere(tvec_R != None)[0][0]        
        nL = n - kL - 1
        nR = n + kR + 1        
        alpha = (hbins[n] - hbins[nL]) / (hbins[nR] - hbins[nL])
        tc = hbins_t[nL] + alpha * (hbins_t[nR] - hbins_t[nL])
        hbins_tfix[n] = tc
hbins_t = hbins_tfix


#### Visualize the results

def smooth(y, kernel_sz):
    #K = np.ones(kernel_sz)
    K = np.hanning(kernel_sz + 2)[1 : -1]
    K = K / np.sum(K)
    y_smooth = np.convolve(y, K, mode='same')
    return y_smooth

def plot_with_dates(tvec, xvec, title_str, label, fig_id=None, style='-',
                    linewidth=1, dt=15):
    fig = plt.figure(fig_id)
    ax = fig.add_subplot(1,1,1)
    plt.xticks(rotation=70)
    plt.plot([], [])
    plt.plot(tvec, xvec, style, linewidth=linewidth, label=label)
    plt.xlabel('Days')
    plt.legend()
    plt.title(title_str)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=dt))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    

perc_photo_act[np.isnan(perc_photo_act)] = 0
perc_z_photo[np.isnan(perc_z_photo)] = 0
#perc_warz_warphoto[np.isnan(perc_warz_warphoto)] = 0

col = 'r'

#dt = 15
dt = 500

m = 1
n = 1

#M = -32
M = -1

#t_limits = (datetime.date(2021, 10, 21), datetime.date(2022, 5, 30))
t_limits = (datetime.date(2008, 1, 1), datetime.date(2023, 5, 1))

# Plot number of active users
plot_with_dates(hbins_t[1:M], h_active[:M], fig_id=2010 + m, style=f'{col}', linewidth=1,
                title_str='Number of active users', label=GROUP_NAME, dt=dt)
plt.xlim(t_limits)
# Plot percentage of active users
plot_with_dates(hbins_t[1:M], perc_active[:M], fig_id=2050 + n, style=f'{col}', linewidth=1,
            title_str='Percentage of active users', label=GROUP_NAME, dt=dt)
plt.xlim(t_limits)
#plt.ylim((0, 1))

# Plot number of users with photo
plot_with_dates(hbins_t[1:M], h_photo[:M], fig_id=1010 + m, style=f'{col}', linewidth=1,
                title_str='Number of users with photo', label=GROUP_NAME, dt=dt)
plt.xlim(t_limits)
# Plot percentage of users with photo (# photo / # active)
plot_with_dates(hbins_t[1:M], perc_photo_act[:M], fig_id=1050 + n, style=f'{col}', linewidth=1,
                title_str='Percentage of users with photo ( / active)', label=GROUP_NAME, dt=dt)
plt.xlim(t_limits)
#plt.ylim((0, 1))
# Plot percentage of users with photo (# photo / # all)
plot_with_dates(hbins_t[1:M], perc_photo_all[:M], fig_id=1060 + n, style=f'{col}', linewidth=1,
                title_str='Percentage of users with photo ( / all)', label=GROUP_NAME, dt=dt)
plt.xlim(t_limits)
#plt.ylim((0, 1))

# Plot number of z-users
plot_with_dates(hbins_t[1:M], h_z[:M], fig_id=1022, style=f'{col}:', linewidth=1,
                title_str='Number of z-users', label=GROUP_NAME, dt=dt)
plt.xlim(t_limits)
plot_with_dates(hbins_t[1:M], smooth(h_z[:M], 7), fig_id=1022, style=f'{col}', linewidth=2,
                title_str='Number of z-users', label=f'{GROUP_NAME}_smoothed', dt=dt)
plt.xlim(t_limits)
#plot_with_dates(hbins_t[1:M], smooth(h_z[:M], 7), fig_id=1025, style=f'{col}', linewidth=1,
#                title_str='Number of z-users', label=f'{GROUP_NAME}_smoothed')

# Plot percentage of z-users among users with photo
plot_with_dates(hbins_t[1:M], perc_z_photo[:M], fig_id=1032, style=f'{col}:', linewidth=1,
                title_str='Percentage of z-users', label=GROUP_NAME, dt=dt)
plot_with_dates(hbins_t[1:M], smooth(perc_z_photo[:M], 7), fig_id=1032, style=f'{col}', linewidth=2,
                title_str='Percentage of z-users', label=f'{GROUP_NAME}_smoothed', dt=dt)
plt.xlim(t_limits)

