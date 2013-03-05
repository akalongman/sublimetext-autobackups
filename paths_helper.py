# Helper functions for building backup file paths.

import sublime
import os
import re
import sys

if sublime.platform() == 'windows':
    from .win_helper import WinHelper


class PathsHelper(object):

    @staticmethod
    def get_base_dir():
        settings = sublime.load_settings('AutoBackups.sublime-settings')
        # Configured setting
        backup_dir =  settings.get('backup_dir')

        if backup_dir != '':
            return os.path.expanduser(backup_dir)

        # Windows: <user folder>/My Documents/Sublime Text Backups
        if sublime.platform() == 'windows':
            return os.path.join(
                WinHelper.get_shell_folder('Personal'),
                'Sublime Text Backups')

        # Linux/OSX/other: ~/sublime_backups
        return os.path.expanduser('~/.sublime/backups')

    @staticmethod
    def timestamp_file(filename):

        (filepart, extensionpart) = os.path.splitext(filename)
        return '%s%s' % (
            filepart,
            extensionpart,
            )

    @staticmethod
    def get_backup_path(filepath):
        path = os.path.expanduser(os.path.split(filepath)[0])
        backup_base = PathsHelper.get_base_dir()
        path = PathsHelper.normalise_path(path)
        return os.path.join(backup_base, path)

    @staticmethod
    def normalise_path(path):

        if sublime.platform() != 'windows':
            # remove any leading / before combining with backup_base
            path = re.sub(r'^/', '', path)
            return path

        path = path.replace('/', '\\')


        # windows only: transform C: into just C
        path = re.sub(r'^(\w):', r'\1', path)

        # windows only: transform \\remotebox\share into network\remotebox\share
        path = re.sub(r'^\\\\([\w\-]{2,})', r'network\\\1', path)
        return path
    @staticmethod
    def get_backup_filepath(filepath):

        filename = os.path.split(filepath)[1]

        return os.path.join(PathsHelper.get_backup_path(filepath), PathsHelper.timestamp_file(filename))

