### Dynamics of vk user registration in pro-war groups

Several pro-war VK groups were analyzed. Registration dates of their members were collected, and war-related anomalies in the dates distribution wwere explored.

The results can be found in `results/user_reg_dynamics`.

The workflow can be reproduced by running `user_reg_dynamics.ipynb` in Google Colab. By default, it uses pre-loaded data and doesn't require VK access. The code for re-loading the data from VK is still pressent, but it is likely that API changed since the last run (and an API key is required anyway).


### Detection of group members with z-avatars

Two sets of VK users were explored:
- Members of a pro-war group "putin_z"
- A random sample of 1 million VK users

For each set, about 45k users were randomly selected, and their avatars were analyzed. Of particular interest were the avatars containing letters Z and V ("Z-avatars"). Registration dates of the users were collected and their temporal distribution was compared between the users with and without Z-avatars.

The results can be found in `results/z_avatars`.