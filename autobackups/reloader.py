# @author 		Avtandil Kikabidze
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze aka LONGMAN (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime
import sys
from imp import reload


reload_mods = []
for mod in sys.modules:
    if mod[0:11].lower() == 'autobackups' and sys.modules[mod] != None:
        reload_mods.append(mod)


mod_prefix = 'AutoBackups.autobackups'

mods_load_order = [
    '',

    '.paths_helper'
]

for suffix in mods_load_order:
    mod = mod_prefix + suffix
    if mod in reload_mods:
        reload(sys.modules[mod])
