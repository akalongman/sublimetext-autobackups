sublimetext-autobackup
======================

Sublime Text 2 Auto backup plugin

AutoBackups is a Sublime Text 2 plugin, which automatically save a backup copy every time you save or open (if backup file not exists) a file. (Like DreamWeaver)

When you edit text files (scripts, prose, whatever) you often find yourself wishing for an last version. Ever accidentally deleted a chunk from an important configuration file, or wished you could roll back a document a few hours? This plugin takes a copy of file you open/save and copies it into a backup directory structure, ensuring that you never lose an old version of a file.


## Installation

 * Install [Package Manager][1].
 * Use `Cmd+Shift+P` or `Ctrl+Shift+P` then `Package Control: Install Package`.
 * Look for `AutoBackups` and install it.

If you prefer to install manually, install git, then:

    git clone https://github.com/akalongman/sublimetext-autobackups "<Sublime Text 2 Packages folder>/AutoBackups"

To change where the backups are stored, access the plugin's settings in `Preferences->Package Settings->AutoBackups`.

To see if it's working, open the console with the `View->Show Console` menu item. When you save a file, you should see a line like this, indicating that the file has been backed up:

    Backup saved to: /home/longman/.sublime/backups/etc/hosts


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
