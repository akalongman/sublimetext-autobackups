import os
import re
import sublime


if sublime.platform() == 'windows':
	try:
	    import winreg
	except ImportError:
	    import _winreg

class WinHelper(object):
    @staticmethod
    def _substenv(m):
        return os.environ.get(m.group(1), m.group(0))

    @staticmethod
    def get_shell_folder(name):
        HKCU = winreg.HKEY_CURRENT_USER
        USER_SHELL_FOLDERS = \
            r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
        key = winreg.OpenKey(HKCU, USER_SHELL_FOLDERS)
        ret = winreg.QueryValueEx(key, name)
        key.Close()
        if ret[1] == winreg.REG_EXPAND_SZ and '%' in ret[0]:
            return re.compile(r'%([^|<>=^%]+)%').sub(_substenv, ret[0])
        else:
            return ret[0]
