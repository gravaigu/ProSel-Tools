#!/usr/bin/env python3

"""
ProSel-Tools backupset

Class to access a ProSel Backup discs set

2022-05-24 : V0.1   Initial version
"""

__version__ = '0.1'
__author__ = 'Eric Le Bras'

import glob

class BackupSet:

    def __init__(self, setglob) -> None:
        discs = glob.glob(setglob)
        discs.sort()

