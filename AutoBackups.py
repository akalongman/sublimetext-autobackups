#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import sys
import os
import shutil
import re

st_version = 2
if sublime.version() == '' or int(sublime.version()) > 3000:
	st_version = 3


reloader_name = 'autobackups.reloader'
if st_version == 3:
	reloader_name = 'AutoBackups.' + reloader_name
	from imp import reload

if reloader_name in sys.modules:
	reload(sys.modules[reloader_name])


try:
	# Python 3
	from AutoBackups.autobackups import reloader
	from AutoBackups.autobackups.paths_helper import PathsHelper
except (ImportError):
	# Python 2
	import autobackups.reloader
	from autobackups.paths_helper import PathsHelper

cprint = globals()["__builtins__"]["print"]

class AutoBackupsEventListener(sublime_plugin.EventListener):

	def getSettings(self):
		platform = sublime.platform().title()
		settings = sublime.load_settings('AutoBackups ('+platform+').sublime-settings')
		return settings


	def on_post_save(self, view):
		if (st_version == 3):
			return
		self.save_backup(view, 0)

	def on_load(self, view):
		if (st_version == 3):
			return
		settings = self.getSettings()
		if settings.get('backup_on_open_file'):
			self.save_backup(view, 1)

	def on_post_save_async(self, view):
		self.save_backup(view, 0)

	def on_load_async(self, view):
		settings = self.getSettings()
		if settings.get('backup_on_open_file'):
			self.save_backup(view, 1)

	def save_backup(self, view, on_load_event):
		settings = self.getSettings()
		# don't save files above configured size
		if view.size() > settings.get('max_backup_file_size_bytes'):
			self.console('Backup not saved, file too large (%d bytes)' % view.size())
			return

		filename = view.file_name()
		newname = PathsHelper.get_backup_filepath(filename)
		if newname == None:
			return
		# not create file backup if current file is backup

		if on_load_event & self.is_backup_file(filename):
			return

		# not create file if exists

		if on_load_event & os.path.isfile(newname):
			return

		(backup_dir, file_to_write) = os.path.split(newname)

		# not create file backup on open event if current file is backup

		if os.access(backup_dir, os.F_OK) == False:
			os.makedirs(backup_dir)

		shutil.copy(filename, newname)

		self.console('Backup saved to: '+newname.replace('\\', '/'))

	def is_backup_file(self, path):
		path = PathsHelper.normalise_path(path)
		base_dir = PathsHelper.get_base_dir(False)
		base_dir = PathsHelper.normalise_path(base_dir)
		backup_dir_len = len(base_dir)
		sub = path[0:backup_dir_len]

		if sub == base_dir:
			return True
		else:
			return False

	def console(self, text):
		cprint(text)


class AutoBackupsOpenBackupCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		platform = sublime.platform().title()
		settings = sublime.load_settings('AutoBackups ('+platform+').sublime-settings')
		backup_per_day = settings.get('backup_per_day')

		if (not backup_per_day):
			window = sublime.active_window()
			view = sublime.Window.active_view(window)
			filepath = view.file_name()
			newname = PathsHelper.get_backup_filepath(filepath)
			if os.path.isfile(newname):
				window.open_file(newname)
			else:
				sublime.error_message('Backup for ' + filepath + ' not exists!')
		else:
			f_files = self.getFiles()

			if not f_files:
				sublime.error_message('Backups for this file not exists!')
				return

			f_files.reverse()
			self.view.window().show_quick_panel(f_files, self.open)
			return

	def getFiles(self):
		filename = PathsHelper.normalise_path(self.view.file_name(), True)
		basedir = PathsHelper.get_base_dir(True)

		f_files = []
		for folder in os.listdir(basedir):
			fl = basedir+'/'+folder+'/'+filename
			match = re.search(r"[0-9+]{4}-[0-9+]{2}-[0-9+]{2}", folder)
			if os.path.isfile(fl) and match is not None:
				folder_name, file_name = os.path.split(fl)
				f_file = []
				f_file.append(folder+' - '+file_name)
				f_file.append(fl)
				f_files.append(f_file)
		return f_files

	def open(self, file):
		if (file == -1):
			return
		# open file
		f_files = self.getFiles()
		filename = f_files[file][1]
		window = sublime.active_window()
		view = sublime.Window.active_view(window)
		window.open_file(filename)

