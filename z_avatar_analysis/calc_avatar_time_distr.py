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
FPATHS_Z = [r'D:\WORK\zresult\putin_z\avatars\putin_z_z']
GROUP_NAME = 'putin_z'

# =============================================================================
# FPATH_USERS_INFO = r'D:\WORK\zresult\random_around_24Feb\users.pkl'
# FPATHS_Z = [r'D:\WORK\zresult\random_around_24Feb\avatars\random_around_24Feb_z']
# GROUP_NAME = 'random'
# =====================================================s========================


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
mask = (user_idx > USER_ID_RANGE[0]) & (user_idx < USER_ID_RANGE[1])
#user_idx = user_idx[mask]

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

# Count users
Nsampled = len(user_idx)
Nactive = len(user_idx_active)
Nphoto = len(user_idx_photo)

# Print summary
print(f'Total: {Nsampled}')
print(f'Active: {Nactive}, {Nactive / Nsampled}')
print(f'With photo: {Nphoto}, {Nphoto / Nactive}')


#### Find users with z-avatars

# Get indices of z-users from filenames
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

# Histogram and percentage of users having avatars
h_photo, _ = np.histogram(user_idx_photo, hbins)
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
perc_z_photo = h_z / h_photo
perc_warz_warphoto = h_war_z / h_war_photo


#### Convert histogram bins from user idx to dates

# User ID -> Rregistration date
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

# =============================================================================
# # Plot histogram of active users
# plt.figure(100); plt.clf()
# plt.plot(hbins[1:], h_active_norm, label='active')
# plt.legend()
# plt.xlabel('User ID')
# plt.title('Histogram of active users')
# =============================================================================

# =============================================================================
# # Plot percentage of active users with photo
# plt.figure(101); plt.clf()
# plt.plot(hbins[1:], perc_photo_act)
# plt.xlabel('User ID')
# plt.title('Percentage of active users with photo')
# =============================================================================
    
def plot_with_dates(tvec, xvec, title_str, label, fig_id=None, style='-', linewidth=1):
    fig = plt.figure(fig_id)
    ax = fig.add_subplot(1,1,1)
    plt.xticks(rotation=70)
    plt.plot([], [])
    plt.plot(tvec, xvec, style, linewidth=linewidth, label=label)
    plt.xlabel('Days')
    plt.legend()
    plt.title(title_str)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    

perc_z_photo[np.isnan(perc_z_photo)] = 0
perc_warz_warphoto[np.isnan(perc_warz_warphoto)] = 0

#col = 'b'
col = 'r'

# Plot number of users with photo
plot_with_dates(hbins_t[1:], h_photo, fig_id=1011, style=f'{col}', linewidth=1,
                title_str='Number of users with photo', label=GROUP_NAME)

# Plot number of z-users
plot_with_dates(hbins_t[1:], h_z, fig_id=1021, style=f'{col}:', linewidth=1,
                title_str='Number of z-users', label=GROUP_NAME)
plot_with_dates(hbins_t[1:], smooth(h_z, 7), fig_id=1021, style=f'{col}', linewidth=2,
                title_str='Number of z-users', label=f'{GROUP_NAME}_smoothed')
plot_with_dates(hbins_t[1:], smooth(h_z, 7), fig_id=1025, style=f'{col}', linewidth=1,
                title_str='Number of z-users', label=f'{GROUP_NAME}_smoothed')

# Plot percentage of z-users among users with photo
plot_with_dates(hbins_t[1:], perc_z_photo, fig_id=1031, style=f'{col}:', linewidth=1,
                title_str='Percentage of z-users', label=GROUP_NAME)
plot_with_dates(hbins_t[1:], smooth(perc_z_photo, 7), fig_id=1031, style=f'{col}', linewidth=2,
                title_str='Percentage of z-users', label=f'{GROUP_NAME}_smoothed')

# =============================================================================
# fig = plt.figure(1030)
# ax = fig.add_subplot(1,1,1)
# plt.xticks(rotation=70)
# plt.plot([], [])
# #plt.plot(hbins_t[1:], perc_z_photo, label=GROUP_NAME)
# plt.plot(hbins_t[1:], smooth(perc_z_photo, 7), label=GROUP_NAME)
# plt.xlabel('Days')
# plt.legend()
# plt.title('Percentage of z-users')
# ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
# =============================================================================

# =============================================================================
# # Plot percentage of users seen during the war (with photo)
# plt.figure(101);
# #plt.plot(hbins_t[1:], perc_warphoto_photo, label=GROUP_NAME)
# plt.plot(hbins_t[1:], h_war_photo, label=GROUP_NAME)
# plt.xlabel('Days')
# plt.legend()
# #plt.title('Percentage of users seen during the war (with photo)')
# plt.title('Number of users seen during the war (with photo)')
# 
# # Plot percentage of users seen during the war (with photo)
# plt.figure(106);
# #plt.plot(hbins_t[1:], perc_warphoto_photo, label=GROUP_NAME)
# plt.plot(hbins_t[1:], h_war_z, label=GROUP_NAME)
# plt.xlabel('Days')
# plt.legend()
# #plt.title('Percentage of users seen during the war (with photo)')
# plt.title('Number of z-users')
# 
# # Plot percentage of z-users
# fig = plt.figure(104);
# ax = fig.add_subplot(1,1,1)
# plt.xticks(rotation=70)
# #plt.plot(hbins_t[1:], perc_z_photo, label='All')
# #plt.plot(hbins_t[1:], perc_warz_warphoto, label='Seen after Feb 24')
# #plt.plot(hbins_t[1:], perc_warz_warphoto, label='putin_z')
# plt.plot(hbins[1:], smooth(perc_warz_warphoto, 5), label=GROUP_NAME)
# plt.xlabel('Days')
# plt.legend()
# plt.title('Percentage of z-users')
# ax.xaxis.set_major_locator(mdates.DayLocator(interval=15))
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
# =============================================================================




# =============================================================================
# 
# def select_interval(x, interval):
#     return x[(x > interval[0]) & (x < interval[1])]
# 
# intervals = [
#         (-1, 707000000),
#         (707000000, 723000000),
#         (723000000, 728700000)
#         ]
# 
# for interval in intervals:
#     
#     user_idx_ = select_interval(user_idx, interval)
#     user_idx_active_ = select_interval(user_idx_active, interval)
#     user_idx_inactive_ = select_interval(user_idx_inactive, interval)
#     user_idx_deleted_ = select_interval(user_idx_deleted, interval)
#     user_idx_banned_ = select_interval(user_idx_banned, interval)
#     user_idx_last_seen_ = select_interval(user_idx_last_seen, interval)
#     user_idx_photo_ = select_interval(user_idx_photo, interval)
#     user_idx_seen_during_war_ = select_interval(
#             user_idx_seen_during_war, interval)
#     user_idx_photo_seen_during_war_ = select_interval(
#             user_idx_photo_seen_during_war, interval)
#     user_idx_z_ = select_interval(user_idx_z, interval)
#     
#     print(f'\n\n==== [{interval[0]} - {interval[1]}] ====\n')
#     print(f'Active: {len(user_idx_active_) / len(user_idx_) : .02f}')
#     print(f'Inctive: {len(user_idx_inactive_) / len(user_idx_) : .02f}')
#     print(f'Deleted / Inactive: '
#           f'{len(user_idx_deleted_) / len(user_idx_inactive_) : .02f}')
#     print(f'Banned / Inactive: '
#           f'{len(user_idx_banned_) / len(user_idx_inactive_) : .02f}')
#     print(f'With_photo / Active: '
#           f'{len(user_idx_photo_) / len(user_idx_active_) : .02f}')
#     print(f'Seen_after_24 / Active: '
#           f'{len(user_idx_seen_during_war_) / len(user_idx_active_) : .02f}')
#     print(f'Seen_after_24 / Active_seen: '
#           f'{len(user_idx_seen_during_war_) / len(user_idx_last_seen_) : .02f}')
#     print(f'Z-photo / Seen_after_24: '
#           f'{len(user_idx_z_) / len(user_idx_seen_during_war_) : .06f}')
#     print(f'Z-photo / Seen_after_24_with_photo: '
#           f'{len(user_idx_z_) / len(user_idx_photo_seen_during_war_) : .06f}')
#     print(f'Z-photo / Active: '
#           f'{len(user_idx_z_) / len(user_idx_active_) : .06f}')
#     print(f'Z-photo / With_photo: '
#           f'{len(user_idx_z_) / len(user_idx_photo_) : .06f}')
# =============================================================================
