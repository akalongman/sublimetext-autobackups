##
# This file is part of the AutoBackups package.
#
# (c) Avtandil Kikabidze aka LONGMAN <akalongman@gmail.com>
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
##

import sublime
import os
import re
import sys
import datetime


backup_name_mode_text = 'auto-save'

class PathsHelper(object):
    platform = False
    backup_dir = False
    backup_per_day = False
    backup_per_time = False
    backup_name_mode = False


    @staticmethod
    def initialize(pl, backup_dir, backup_per_day, backup_per_time, backup_name_mode):
        PathsHelper.platform = pl
        PathsHelper.backup_dir = backup_dir
        PathsHelper.backup_per_day = backup_per_day
        PathsHelper.backup_per_time = backup_per_time
        PathsHelper.backup_name_mode = backup_name_mode


    @staticmethod
    def get_base_dir(only_base):
        # Configured setting
        backup_dir = PathsHelper.backup_dir
        now_date = str(datetime.datetime.now())
        date = now_date[:10]

        backup_per_day = PathsHelper.backup_per_day
        if (backup_per_day and not only_base):
            backup_dir = backup_dir +'/'+ date

        time = now_date[11:19].replace(':', '')
        backup_per_time = PathsHelper.backup_per_time
        if (backup_per_day and backup_per_time == 'folder' and not only_base):
            backup_dir = backup_dir +'/'+ time

        if backup_dir != '':
            return os.path.expanduser(backup_dir)

        # Windows: <user folder>/My Documents/Sublime Text Backups
        if (PathsHelper.platform == 'Windows'):
            backup_dir = 'D:/Sublime Text Backups'
            if (backup_per_day and not only_base):
                backup_dir = backup_dir +'/'+ date
            return backup_dir

        # Linux/OSX/other: ~/sublime_backups
        backup_dir = '~/.sublime/backups'
        if (backup_per_day and not only_base):
            backup_dir = backup_dir +'/'+ date
        return os.path.expanduser(backup_dir)

    @staticmethod
    def create_name_file(filename):
        (filepart, extensionpart) = os.path.splitext(filename)

        if PathsHelper.backup_name_mode not in (False, None, ) \
          and PathsHelper.backup_name_mode.lower() == 'prefix':
            filepart = '%s.%s' % (backup_name_mode_text, filepart)

        backup_per_day =  PathsHelper.backup_per_day
        backup_per_time =  PathsHelper.backup_per_time
        if (backup_per_day and backup_per_time == 'file'):
            now_date = str(datetime.datetime.now())
            time = now_date[11:19].replace(':', '')
            name = '%s_%s%s' % (filepart, time, extensionpart,)
        else:
            name = '%s%s' % (filepart, extensionpart,)

        (filepart, extensionpart) = os.path.splitext(name) 
        if PathsHelper.backup_name_mode not in (False, None, ) \
          and PathsHelper.backup_name_mode.lower() == 'suffix':
            name = '%s.%s%s' % (filepart, backup_name_mode_text, extensionpart)
        return name

    @staticmethod
    def get_backup_path(filepath):
        path = os.path.expanduser(os.path.split(filepath)[0])
        backup_base = PathsHelper.get_base_dir(False)
        path = PathsHelper.normalise_path(path)
        return os.path.join(backup_base, path)

    @staticmethod
    def normalise_path(path, slashes = False):
        if (path is None):
            return ''

        if PathsHelper.platform != 'Windows':
            # remove any leading / before combining with backup_base
            path = re.sub(r'^/', '', path)
            return path

        path = path.replace('/', '\\')


        # windows only: transform C: into just C
        path = re.sub(r'^(\w):', r'\1', path)

        # windows only: transform \\remotebox\share into network\remotebox\share
        path = re.sub(r'^\\\\([\w\-]{2,})', r'network\\\1', path)

        if slashes:
            path = path.replace('\\', '/')

        return path



    @staticmethod
    def get_backup_filepath(filepath):
        filename = os.path.split(filepath)[1]
        return os.path.join(PathsHelper.get_backup_path(filepath), PathsHelper.create_name_file(filename))

