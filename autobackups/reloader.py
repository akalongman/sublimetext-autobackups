##
# This file is part of the AutoBackups package.
#
# (c) Avtandil Kikabidze aka LONGMAN <akalongman@gmail.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
##

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
