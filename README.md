# ProSel Tools

Tools to manipulate data from Apple IIGS ProSel backup disk images.

## The story

Thirty years passed since I had stopped using my Apple IIGS. Lastly I took it out of the closet. I wanted to recover the files that once were on the hard disk. Then I got my hands on a stack of 3.5 floppies labeled "Salvation Backup". My attempts to revover the files were in vain, so I decided to have a look at the floppies content, and try to reverse engeneer the backup process. I transfered the floppies to PC, and after some hours analyzing the bytes I had a Python script that could extract the individual files from the floppies images.

That's when I realized that, despite being labeled "Salvation Backup", in reality the disks had been written by another popular GS tool of the time: ProSel-16 backup :-) Indeed, the restoration process with ProSel-16 Restore on the IIGS was a success!

Anyway, the Python script exists and is also very functionnal. It can extract the files as regular Linux files, or as AppleSingle files (with ProDOS file metadata and resource fork if present). The resulting files (regular or AppleSingle), may then be passed to AppleCommander, if you wish to put them on a ProDOS image.

## The scripts

**prosel-restore.py** The tool to list/extract data from ProSel-16 Backup floppies. Note that the tool is built for backups made with ProSel-16 version 8.2 and newer. Run `./prosel-restore.py --help` for usage documentation.

**make-image.py** Takes an AppleSingle file hierarchy (created with *prosel-restore.py*) and put it on ProDOS image, using *AppleCommander*. This script needs some refactoring!
