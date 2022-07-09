#!/usr/bin/env python3

"""
BakkupCat class
Read Catalog disk

2022-05-31 : V0.1   Initial version
"""

__version__ = '0.1'
__author__ = 'Eric Le Bras'

from multiprocessing.dummy import Array
from tokenize import String


class BakkupCat:
    """
    Salvation Bakkup disk TOC
    """

    def __init__(self, disc) -> None:
        self.cat = []
        with open(disc, 'rb') as f:
            buffer = f.read(512*12) # Sauter les 12 premiers blocs
            buffer = f.read(74) # Entête
            self.nfiles = int.from_bytes(buffer[50:52], 'little')
            n = self.nfiles
            while (n > 0):
                buffer = f.read(74)     # Data fichier (1)
                entree = {'name_len':int.from_bytes(buffer[9:11], 'little')}
                entree['filename'] = buffer[11:11+entree['name_len']].decode('ascii')
                entree['filetype'] = buffer[42]
                entree['filelen'] = int.from_bytes(buffer[44:47], 'little')
                entree['nelem'] = int.from_bytes(buffer[48:50], 'little')
                entree['csec'] = buffer[52]
                entree['cmin'] = buffer[53]
                entree['chour'] = buffer[54]
                entree['cyear'] = buffer[55]
                entree['cday'] = buffer[56]
                entree['cmonth'] = buffer[57]
                entree['msec'] = buffer[60]
                entree['mmin'] = buffer[61]
                entree['mhour'] = buffer[62]
                entree['myear'] = buffer[63]
                entree['mday'] = buffer[64]
                entree['mmonth'] = buffer[65]
                self.cat.append(entree)
                if entree['filetype'] != 0x0F:
                    n -= 1

    # def get_vol_name(self) -> String:
    #     return self.vol_name
    
    def get_content(self) -> Array:
        return self.cat

if __name__ == '__main__':
    # Print catalog and leave
    bakkupCat = BakkupCat('/home/eric/Apple2/gs_drive/salvation_backup/salvationcatalog.po')
    for entree in bakkupCat.get_content():
        print(entree)
