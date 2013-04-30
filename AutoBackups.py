#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sublime
import sublime_plugin
import sys
import os
import shutil

reloader_name = 'AutoBackups.autobackups.reloader'
from imp import reload
if reloader_name in sys.modules:
	reload(sys.modules[reloader_name])

from AutoBackups.autobackups import reloader
from AutoBackups.autobackups.paths_helper import PathsHelper



class AutoBackupsEventListener(sublime_plugin.EventListener):
	platform = sublime.platform().title()
	settings = sublime.load_settings('AutoBackups ('+platform+').sublime-settings')

	def on_post_save_async(self, view):
		self.save_backup(view, 0)

	def on_load_async(self, view):
		#settings = sublime.load_settings('AutoBackups.sublime-settings')
		if self.settings.get('backup_on_open_file'):
			self.save_backup(view, 1)

	def save_backup(self, view, on_load_event):
		# don't save files above configured size
		if view.size() > self.settings.get('max_backup_file_size_bytes'):
			print ('Backup not saved, file too large (%d bytes)' % view.size())
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


		print ('Backup saved to:', newname.replace('\\', '/'))

	def is_backup_file(self, path):
		path = PathsHelper.normalise_path(path)
		base_dir = PathsHelper.get_base_dir()
		base_dir = PathsHelper.normalise_path(base_dir)
		backup_dir_len = len(base_dir)
		sub = path[0:backup_dir_len]

		if sub == base_dir:
			return True
		else:
			return False


class AutoBackupsOpenBackupCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		window = sublime.active_window()
		view = sublime.Window.active_view(window)
		filepath = view.file_name()
		newname = PathsHelper.get_backup_filepath(filepath)

		if os.path.isfile(newname):
			window.open_file(newname)
		else:
			sublime.error_message('Backup for ' + filepath + ' not exists!')
