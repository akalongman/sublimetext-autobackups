# Helper functions for building backup file paths.

import sublime
import os
import re

if sublime.platform() == 'windows':
    import win32helpers

settings = sublime.load_settings('AutoBackups.sublime-settings')


def get_base_dir():

    # Configured setting
    backup_dir = settings.get('backup_dir', '')
    if backup_dir != '':
        return os.path.expanduser(backup_dir)

    # Windows: <user folder>/My Documents/Sublime Text Backups
    if sublime.platform() == 'windows':
        return os.path.join(
            win32helpers.get_shell_folder('Personal'),
            'Sublime Text Backups')

    # Linux/OSX/other: ~/sublime_backups
    return os.path.expanduser('~/.sublime/backups')


def timestamp_file(filename):

    (filepart, extensionpart) = os.path.splitext(filename)
    return '%s%s' % (
        filepart,
        extensionpart,
        )

def get_backup_path(filepath):

    path = os.path.expanduser(os.path.split(filepath)[0])
    backup_base = get_base_dir()
    path = normalise_path(path)
    return os.path.join(backup_base, path)

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

def get_backup_filepath(filepath):

    filename = os.path.split(filepath)[1]

    return os.path.join(get_backup_path(filepath), timestamp_file(filename))
