# Sublime Text 2 event listeners and commands interface for automatic backups.

import sublime
import sublime_plugin
import os
import shutil

import backup_paths

settings = sublime.load_settings('AutoBackups.sublime-settings')


class AutoBackupsEventListener(sublime_plugin.EventListener):

    """Creates an automatic backup of every file you save. This
    gives you a rudimentary mechanism for making sure you don't lose
    information while working."""

    def on_post_save(self, view):
        """When a file is saved, put a copy of the file into the
        backup directory."""

        # don't save files above configured size
        if view.size() > settings.get("max_backup_file_size_bytes"):
            print 'Backup not saved, file too large (%d bytes)' % view.size()
            return

        filename = view.file_name()
        newname = backup_paths.get_backup_filepath(filename)
        if newname == None:
            return

        (backup_dir, file_to_write) = os.path.split(newname)

        # make sure that we have a directory to write into
        if os.access(backup_dir, os.F_OK) == False:
            os.makedirs(backup_dir)

        shutil.copy(filename, newname)
        print 'Backup saved to:', newname
