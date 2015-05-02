# @author 		Avtandil Kikabidze
# @copyright 		Copyright (c) 2008-2014, Avtandil Kikabidze aka LONGMAN (akalongman@gmail.com)
# @link 			http://long.ge
# @license 		GNU General Public License version 2 or later;

import sublime
import sublime_plugin
import sys
import os
import shutil
import re
import hashlib
import time
import threading

st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
	st_version = 3


reloader_name = 'autobackups.reloader'
if st_version == 3:
	reloader_name = 'AutoBackups.' + reloader_name
	from imp import reload

if reloader_name in sys.modules:
	reload(sys.modules[reloader_name])

# fix for ST2
cprint = globals()["__builtins__"]["print"]



try:
	# Python 3
	from AutoBackups.autobackups import reloader
	from AutoBackups.autobackups.paths_helper import PathsHelper
except (ImportError):
	# Python 2
	import autobackups.reloader
	from autobackups.paths_helper import PathsHelper


def plugin_loaded():
	global settings
	global hashes

	hashes = {}
	platform = sublime.platform().title()

	if (platform == "Osx"):
		platform = "OSX"
	settings = sublime.load_settings('AutoBackups ('+platform+').sublime-settings')

	backup_dir = settings.get('backup_dir')
	backup_per_day = settings.get('backup_per_day')
	backup_per_time = settings.get('backup_per_time')

	PathsHelper.initialize(platform, backup_dir, backup_per_day, backup_per_time)
	cprint('AutoBackups: Plugin Initialized')
	sublime.set_timeout(gc, 10000)





def gc():
	backup_time = settings.get('delete_old_backups', 0)
	if (backup_time > 0):
		thread = AutoBackupsGcBackup(backup_time)
		thread.start()


class AutoBackupsEventListener(sublime_plugin.EventListener):

	def on_post_save(self, view):
		if (st_version == 3):
			return
		self.save_backup(view, 0)

	def on_load(self, view):
		if (st_version == 3):
			return

		if settings.get('backup_on_open_file'):
			self.save_backup(view, 1)


	def on_post_save_async(self, view):
		self.save_backup(view, 0)


	def on_load_async(self, view):
		if settings.get('backup_on_open_file'):
			self.save_backup(view, 1)


	def save_backup(self, view, on_load_event):

		if (view.is_read_only()):
			return

		view_size = view.size()
		max_backup_file_size = settings.get('max_backup_file_size_bytes')
		if (view_size is None):
			self.console('Size of view not available')
			return

		if (max_backup_file_size is None):
			self.console('Max allowed size from config not available')
			return


		# don't save files above configured size
		if view_size > max_backup_file_size:
			self.console('Backup not saved, file too large (%d bytes)' % view.size())
			return


		filename = view.file_name()
		if filename == None:
			return

		# Check file path in excluded regexes
		if self.is_excluded(filename):
			#cprint("AutoBackups: " + filename + " is excluded");
			return



		# not create file backup if current file is backup
		if on_load_event & self.is_backup_file(filename):
			return


		newname = PathsHelper.get_backup_filepath(filename)
		if newname == None:
			return

		buffer_id = view.buffer_id()
		content = filename+view.substr(sublime.Region(0, view_size))
		content = self.encode(content)
		current_hash = hashlib.md5(content).hexdigest()

		last_hash = ''
		try:
			last_hash = hashes[buffer_id]
		except Exception as e:
			last_hash = ''


		# not create file backup if no changes from last backup
		if (last_hash == current_hash):
			return

		# not create file if exists
		if on_load_event & os.path.isfile(newname):
			return

		(backup_dir, file_to_write) = os.path.split(newname)

		if os.access(backup_dir, os.F_OK) == False:
			os.makedirs(backup_dir)

		shutil.copy(filename, newname)

		hashes[buffer_id] = current_hash
		self.console('Backup saved to: '+newname.replace('\\', '/'))

	def is_backup_file(self, path):
		backup_per_time = settings.get('backup_per_time')
		path = PathsHelper.normalise_path(path)
		base_dir = PathsHelper.get_base_dir(False)
		base_dir = PathsHelper.normalise_path(base_dir)
		if (backup_per_time == 'folder'):
			base_dir = base_dir[:-7]

		backup_dir_len = len(base_dir)
		sub = path[0:backup_dir_len]

		if sub == base_dir:
			return True
		else:
			return False

	def is_excluded(self, filename):
		# check
		ignore_regexes = settings.get('ignore_regexes')

		if (ignore_regexes is None or ignore_regexes == ""):
			return False

		for regex in ignore_regexes:
			prog = re.compile('.*'+regex+'.*')
			result = prog.match(filename)
			if result is not None:
				return True

		return False


	def console(self, text):
		cprint(text)

	def fileChanged(self, text):
		return

	def encode(self, text):
		if (st_version == 2):
			if isinstance(text, unicode):
				text = text.encode('UTF-8')
		elif (st_version == 3):
			if isinstance(text, str):
				text = text.encode('UTF-8')
		return text




class AutoBackupsOpenBackupCommand(sublime_plugin.TextCommand):
	datalist = []
	curline = 1

	def run(self, edit):
		backup_per_day = settings.get('backup_per_day')

		window = self.view.window()
		view = self.view

		open_in_same_line = settings.get('open_in_same_line', True)
		if (open_in_same_line):
			(row,col) = view.rowcol(view.sel()[0].begin())
			self.curline = row + 1


		if (not backup_per_day):
			filepath = view.file_name()
			newname = PathsHelper.get_backup_filepath(filepath)
			if os.path.isfile(newname):
				window.open_file(newname)
			else:
				sublime.error_message('Backup for ' + filepath + ' not exists!')
		else:
			f_files = self.getData(False)

			if not f_files:
				sublime.error_message('Backups for this file not exists!')
				return

			backup_per_time = settings.get('backup_per_time')
			if (backup_per_time):
				window.show_quick_panel(f_files, self.timeFolders)
			else:
				window.show_quick_panel(f_files, self.openFile)
			return




	def getData(self, time_folder):
		filename = PathsHelper.normalise_path(self.view.file_name(), True)
		basedir = PathsHelper.get_base_dir(True)

		backup_per_time = settings.get('backup_per_time')
		if (backup_per_time):
			if (backup_per_time == 'folder'):
				f_files = []
				if (time_folder is not False):
					tm_folders = self.getData(False)
					tm_folder = tm_folders[time_folder][0]
					basedir = basedir+'/'+tm_folder

					if (not os.path.isdir(basedir)):
						sublime.error_message('Folder ' + basedir + ' not found!')

					for folder in os.listdir(basedir):
						fl = basedir+'/'+folder+'/'+filename
						match = re.search(r"^[0-9+]{6}$", folder)
						if os.path.isfile(fl) and match is not None:
							folder_name, file_name = os.path.split(fl)
							f_file = []
							time = self.formatTime(folder)
							f_file.append(time+' - '+file_name)
							f_file.append(fl)
							f_files.append(f_file)
				else:
					path, flname = os.path.split(filename)
					(filepart, extpart) = os.path.splitext(flname)
					for folder in os.listdir(basedir):
						match = re.search(r"^[0-9+]{4}-[0-9+]{2}-[0-9+]{2}$", folder)
						if match is not None:
							folder_name, file_name = os.path.split(filename)
							f_file = []
							basedir2 = basedir+'/'+folder
							count = 0
							last = ''
							for folder2 in os.listdir(basedir2):
								match = re.search(r"^[0-9+]{6}$", folder2)
								if match is not None:
									basedir3 = basedir+'/'+folder+'/'+folder2+'/'+filename
									if os.path.isfile(basedir3):
										count += 1
										last = folder2
							if (count > 0):
								f_file.append(folder)
								f_file.append('Backups: '+str(count)+', Last edit: '+self.formatTime(last))
								f_files.append(f_file)
			elif (backup_per_time == 'file'):
				f_files = []
				if (time_folder is not False):
					tm_folders = self.getData(False)
					tm_folder = tm_folders[time_folder][0]
					path, flname = os.path.split(filename)
					basedir = basedir+'/'+tm_folder+'/'+path
					(filepart, extpart) = os.path.splitext(flname)

					if (not os.path.isdir(basedir)):
						sublime.error_message('Folder ' + basedir + ' not found!')

					for folder in os.listdir(basedir):
						fl = basedir+'/'+folder
						match = re.search(r"^"+re.escape(filepart)+"_([0-9+]{6})"+re.escape(extpart)+"$", folder)

						if os.path.isfile(fl) and match is not None:
							time = self.formatTime(match.group(1))
							f_file = []
							f_file.append(time+' - '+flname)
							f_file.append(fl)
							f_files.append(f_file)
				else:
					path, flname = os.path.split(filename)
					(filepart, extpart) = os.path.splitext(flname)
					for folder in os.listdir(basedir):
						match = re.search(r"^[0-9+]{4}-[0-9+]{2}-[0-9+]{2}$", folder)
						if match is not None:
							folder_name, file_name = os.path.split(filename)
							f_file = []
							basedir2 = basedir+'/'+folder+'/'+path
							count = 0
							last = ''
							if (os.path.isdir(basedir2)):
								for sfile in os.listdir(basedir2):
									match = re.search(r"^"+re.escape(filepart)+"_([0-9+]{6})"+re.escape(extpart)+"$", sfile)
									if match is not None:
										count += 1
										last = match.group(1)
							if (count > 0):
								f_file.append(folder)
								f_file.append('Backups: '+str(count)+', Last edit: '+self.formatTime(last))
								f_files.append(f_file)
		else:
			f_files = []
			for folder in os.listdir(basedir):
				fl = basedir+'/'+folder+'/'+filename
				match = re.search(r"^[0-9+]{4}-[0-9+]{2}-[0-9+]{2}$", folder)
				if os.path.isfile(fl) and match is not None:
					folder_name, file_name = os.path.split(fl)
					f_file = []
					f_file.append(folder+' - '+file_name)
					f_file.append(fl)
					f_files.append(f_file)
		f_files.reverse()
		self.datalist = f_files
		return f_files



	def timeFolders(self, parent):
		if (parent == -1):
			return

		# open file
		f_files = self.getData(parent)
		if (st_version == 3):
			show_previews = settings.get('show_previews', True)
			if (show_previews):
				sublime.set_timeout_async(lambda: self.view.window().show_quick_panel(f_files, self.openFile, on_highlight=self.showFile), 100)
			else:
				sublime.set_timeout_async(lambda: self.view.window().show_quick_panel(f_files, self.openFile), 100)
		else:
			sublime.set_timeout(lambda: self.view.window().show_quick_panel(f_files, self.openFile), 100)

		return

	def showFile(self, file):
		if (file == -1):
			return

		f_files = self.datalist
		filename = f_files[file][1]
		window = self.view.window()

		view = window.open_file(filename+":"+str(self.curline), sublime.ENCODED_POSITION | sublime.TRANSIENT)
		view.set_read_only(True)


	def openFile(self, file):
		if (file == -1):
			window = sublime.active_window()
			window.focus_view(self.view)
			return

		f_files = self.datalist
		filename = f_files[file][1]

		window = self.view.window()
		view = window.open_file(filename+":"+str(self.curline), sublime.ENCODED_POSITION)
		view.set_read_only(True)
		window.focus_view(view)

	def formatTime(self, time):
		time = time[0:2]+':'+time[2:4]+':'+time[4:6]
		return time



class AutoBackupsGcBackup(threading.Thread):
	backup_time = 0

	def __init__(self, back_time):
		self.backup_time = back_time
		threading.Thread.__init__(self)


	def run(self):
		import datetime
		basedir = PathsHelper.get_base_dir(True)
		backup_time = self.backup_time

		if (backup_time < 1):
			return

		diff = (backup_time + 1) * 24 * 3600
		deleted = 0
		now_time = time.time()
		for folder in os.listdir(basedir):
			match = re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", folder)
			if match is not None:
				folder_time = time.mktime(datetime.datetime.strptime(folder, "%Y-%m-%d").timetuple())
				if (now_time - folder_time > diff):
					fldr = basedir+'/'+folder
					try:
						shutil.rmtree(fldr, onerror=self.onerror)
						deleted = deleted + 1
					except Exception as e:
						cprint(e)

		if (deleted > 0):
			diff = backup_time * 24 * 3600
			dt = now_time - diff
			date = datetime.datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
			cprint('AutoBackups: Deleted '+str(deleted)+' backup folders older than '+date)


	def onerror(self, func, path, exc_info):
	    import stat
	    if not os.access(path, os.W_OK):
	        # Is the error an access error ?
	        os.chmod(path, stat.S_IWUSR)
	        func(path)
	    else:
	        raise


class AutoBackupsDonateCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		sublime.message_dialog('AutoBackups: Thanks for your support ^_^')
		browser = settings.get("default_browser", "")
		AutoBackupsOpenInBrowserThread('','').try_open("https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=MVCBM7M2RCEX6&lc=US&item_name=Support%20our%20open%2dsource%20initiatives&item_number=donation&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donate_LG%2egif%3aNonHosted", browser)


class AutoBackupsOpenInBrowserThread(threading.Thread):
	def __init__(self, url, browser):
		self.url = url
		self.browser = browser
		threading.Thread.__init__(self)

	def run(self):
		url = self.url
		browser = self.browser

		self.try_open(url, browser)

	def try_open(self, url, browser):
		import subprocess

		if sublime.platform() == 'windows':
			import winreg

		browser = browser.lower().strip();
		items = []

		if browser == 'chrome':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Google Chrome.app', url]
			elif sublime.platform() == 'windows':
				aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = winreg.QueryValueEx (aKey, "Local AppData")

				items.extend([
					'%HOMEPATH%\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'

					,reg_value+'\\Chrome\\Application\\chrome.exe'
					,reg_value+'\\Google\\Chrome\\Application\\chrome.exe'
					,'%HOMEPATH%\\Google\\Chrome\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Google\\Chrome\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Google\\Chrome\\Application\\chrome.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\chrome.exe'
					,'%HOMEPATH%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Chromium\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome\\Application\\chrome.exe'
					,'chrome.exe'
				])


				commands = ['-new-tab', url]
			else:
				items.extend([
					'/usr/bin/google-chrome'
					,'/opt/google/chrome/chrome'
					,'chrome'
					,'google-chrome'
				])
				commands = ['-new-tab', url]

		elif browser == 'canary':
			if sublime.platform() == 'osx':
					items.extend(['open'])
					commands = ['-a', '/Applications/Google Chrome Canary.app', url]
			elif sublime.platform() == 'windows':
				aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = winreg.QueryValueEx (aKey, "Local AppData")

				items.extend([
					'%HOMEPATH%\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe'

					,reg_value+'\\Chrome SxS\\Application\\chrome.exe'
					,reg_value+'\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%HOMEPATH%\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome SxS\\chrome.exe'
					,'%HOMEPATH%\\Local\ Settings\\Application\ Data\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome SxS\\Application\\chrome.exe'
				])

				commands = ['-new-tab', url]

		elif browser == 'chromium':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Chromium.app', url]
			elif sublime.platform() == 'windows':
				aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = winreg.QueryValueEx (aKey, "Local AppData")
				items.extend([
					'%HOMEPATH%\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe'

					, reg_value+'\\Chromium\\Application\\chromium.exe'
					,'%USERPROFILE%\\Local Settings\\Application Data\\Google\\Chrome\\chromium.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\chromium.exe'
					,'%HOMEPATH%\\Chromium\\Application\\chromium.exe'
					,'%PROGRAMFILES%\\Chromium\\Application\\chromium.exe'
					,'%PROGRAMFILES(X86)%\\Chromium\\Application\\chromium.exe'
					,'%HOMEPATH%\\Local Settings\\Application\ Data\\Google\\Chrome\\Application\\chromium.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome\\Application\\chromium.exe'
					,'chromium.exe'

					, reg_value+'\\Chromium\\Application\\chrome.exe'
					,'%USERPROFILE%\\Local Settings\\Application Data\\Google\\Chrome\\chrome.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\chrome.exe'
					,'%HOMEPATH%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Chromium\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome\\Application\\chrome.exe'
					,'chrome.exe'

				])
				commands = ['-new-tab', url]
			else:
				items.extend([
					'/usr/bin/chromium'
					,'chromium'
					,'/usr/bin/chromium-browser'
					,'chromium-browser'
				])
				commands = ['-new-tab', url]
		elif browser == 'firefox':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Firefox.app', url]
			else:
				items.extend([
					'/usr/bin/firefox'

					,'%PROGRAMFILES%\\Nightly\\firefox.exe'
					,'%PROGRAMFILES(X86)%\\Nightly\\firefox.exe'

					,'%PROGRAMFILES%\\Mozilla Firefox\\firefox.exe'
					,'%PROGRAMFILES(X86)%\\Mozilla Firefox\\firefox.exe'

					,'firefox'
					,'firefox.exe'
				])
				commands = ['-new-tab', url]
		elif browser == 'aurora':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/FirefoxAurora.app', url]
			else:
				items.extend([
					'/usr/bin/aurora'

					,'%PROGRAMFILES%\\Aurora\\firefox.exe'
					,'%PROGRAMFILES(X86)%\\Aurora\\firefox.exe'

					,'firefox'
					,'firefox.exe'
				])
				commands = ['-new-tab', url]
		elif browser == 'opera':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Opera.app', url]
			else:
				items.extend([
					'/usr/bin/opera'
					,'/usr/bin/opera-next'
					,'/usr/bin/operamobile'

					,'%PROGRAMFILES%\\Opera\\opera.exe'
					,'%PROGRAMFILES(X86)%\\Opera\\opera.exe'

					,'%PROGRAMFILES%\\Opera Next\\opera.exe'
					,'%PROGRAMFILES(X86)%\\Opera Next\\opera.exe'

					,'%PROGRAMFILES%\\Opera Mobile Emulator\\OperaMobileEmu.exe'
					,'%PROGRAMFILES(X86)%\\Opera Mobile Emulator\\OperaMobileEmu.exe'

					,'opera'
					,'opera.exe'
				])
				commands = ['-newtab', url]
		elif browser == 'safari':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', 'Safari', url]
			else:
				items.extend([
					'/usr/bin/safari'

					,'%PROGRAMFILES%\\Safari\\Safari.exe'
					,'%PROGRAMFILES(X86)%\\Safari\\Safari.exe'

					,'Safari'
					,'Safari.exe'
				])
				commands = ['-new-tab', '-url', url]
		else:
			commands = ['-new-tab', url]

		for item in items:
			try:
				command2 = list(commands)
				command2.insert(0, expandVars(item))
				subprocess.Popen(command2)
				return
			except:
				try:
					command2 = list(commands)
					command2.insert(0, item)
					subprocess.Popen(command2)
					return
				except:
					pass
		try:
			if sublime.platform() == 'windows':
				commands = ['cmd','/c','start', '', url]
				subprocess.Popen(commands)
			elif sublime.platform() == 'linux':
				commands = ['xdg-open', url]
				subprocess.Popen(commands)
			else:
				commands = ['open', url]
				subprocess.Popen(commands)
			return
		except:
			pass

		sublime.error_message('Can not open PayPal url. Default browser not found..')










if st_version == 2:
	plugin_loaded()