# -*- coding: utf-8 -*-

import vk_utils

vk = vk_utils.VkAPI()

group_id = {'russia'}

# Get group members from vk
members = vk.load_group_members(group_id, ntoload='all', offset=0,
                                sort_type='id_desc', fields=None)
