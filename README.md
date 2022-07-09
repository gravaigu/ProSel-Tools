# ProSel Tools

Tools to manipulate data from Apple IIGS ProSel backup disk images.

## The story

Thirty years passed since I had stopped using my Apple IIGS. Lastly I took it out of the closet. I wanted to recover the files that once were on the hard disk. Then I got my hands on a stack of 3.5 floppies labeled "Salvation Backup". My attempds to revover the files were in vain, so I decided to have a look at the floppies content, and tried to reverse engeneer the backup process. I transfered the floppies to a PC, and after some work I had a Python script that could extract the individual files from the floppies images.

That's when I realized that, despite being labeled "Salvation Backup", in reality the disks had been written with another popular GS tool of the time: ProSel backup :-) Indeed, the restoration process with ProSel Restore on the IIGS was a success!

Anyway, the Python script is writtent and is also very functionnal. It can extract the files as regular Linux files, or as AppleSingle files (with ProDOS file metadata and resource fork if present). The resulting files (regular or AppleSingle), may then be passed to AppleCommander, if you wish to put them on a ProDOS image.