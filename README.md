sublimetext-autobackups
======================

Sublime Text 2/3 Auto backups plugin

AutoBackups is a Sublime Text 2/3 plugin, which automatically save a backup copy every time you save or open (if backup file not exists) a file. (Like DreamWeaver.. No, better than DreamWeaver)

When you edit text files (scripts, prose, whatever) you often find yourself wishing for an last version. Ever accidentally deleted a chunk from an important configuration file, or wished you could roll back a document a few hours? This plugin takes a copy of file you open/save and copies it into a backup directory structure, ensuring that you never lose an old version of a file. If enabled setting backup_per_day backups will be saved for each day. If enabled setting backup_per_time backups will be saved for each save.


### Configuration

To change plugin configuration, access the plugin's settings in `Preferences->Package Settings->AutoBackups`.

Configuration options:
```js
	{
		// The directory where we'll keep our backups. If empty, we'll try to put them in
		// D:/Sublime Text Backups
		"backup_dir": "D:/Sublime Text Backups",

		// If true, also save a backup copy any time a file is opened (if backup file not exists)
		"backup_on_open_file": true,

		// If true, backups saved per day, in separate folders, for example D:/Sublime Text Backups/2013-05-23/myfile.php
		"backup_per_day": true,

		// If set, backups saved per second. NOTE: backup will be saved, if file modified after last backup. possible values: false, "folder" or "file"
		// false - disabled backup per second
		// "folder" - backup example D:/Sublime Text Backups/2013-05-23/095034/myfile.php
		// "file" - backup example D:/Sublime Text Backups/2013-05-23/myfile_095034.php
		// to use this feature, you must have enabled backup_per_day setting
		"backup_per_time": "file",

		// Files larger than this many bytes won't be backed up.
		"max_backup_file_size_bytes": 262144 // = 256 KB
	}
```



## Installation

**With the Package Control plugin:** The easiest way to install AutoBackups is through Package Control, which can be found at this site: https://sublime.wbond.net/installation

Once you install Package Control, restart Sublime Text and bring up the Command Palette (`Command+Shift+P` on OS X, `Control+Shift+P` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select AutoBackups when the list appears. The advantage of using this method is that Package Control will automatically keep AutoBackups up to date with the latest version.

**Without Git:** Download the latest source from [GitHub](https://github.com/akalongman/sublimetext-autobackups) and copy the AutoBackups folder to your Sublime Text "Packages" directory.

**With Git:** Clone the repository in your Sublime Text "Packages" directory:

    git clone https://github.com/akalongman/sublimetext-autobackups.git AutoBackups


The "Packages" directory is located at:

* OS X:

        ST2: ~/Library/Application Support/Sublime Text 2/Packages/
        ST3: ~/Library/Application Support/Sublime Text 3/Packages/

* Linux:

        ST2: ~/.config/sublime-text-2/Packages/
        ST3: ~/.config/sublime-text-3/Packages/

* Windows:

        ST2: %APPDATA%/Sublime Text 2/Packages/
        ST3: %APPDATA%/Sublime Text 3/Packages/



To see if plugin working, open the console with the `View->Show Console` menu item. When you save a file, you should see a line like this, indicating that the file has been backed up:

    Backup saved to: D:/Sublime Text Backups/2013-05-23/myfile_095034.php

## Backup size considerations

To prevent your backup folder from growing too large, check out the `max_backup_file_size_bytes` setting in `Preferences->Package Settings->AutoBackups`.

## Keybindings

To open current file backup, use cmd+alt+b keybinding, or in quick panel type AutoBackup: Open file backup


## Credits

This code is available on [Github][0]. Pull requests are welcome.

Created by [Avtandil Kikabidze][3].

Originally Automatic Backups plugin authored by [Joel Thornton][2].

 [0]: https://github.com/akalongman/sublimetext-autobackups
 [1]: http://wbond.net/sublime_packages/package_control
 [2]: https://github.com/joelpt/sublimetext-automatic-backups
 [3]: mailto:akalongman@gmail.com
