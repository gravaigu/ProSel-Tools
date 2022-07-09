#!/usr/bin/env python3

"""
BackupTOC class

Read ProSel Backup disc table of content

2022-05-31 : V0.1   Initial version
2022-07-09 : V1.0   First revision
"""

__version__ = '0.1'
__author__ = 'Eric Le Bras'

from multiprocessing.dummy import Array
from tokenize import String


class BackupTOC:
    """
    Salvation Backup disk TOC
    """

    def __init__(self, disc) -> None:
        self.toc = []
        with open(disc, 'rb') as f:
            f.seek(0x200)
            buffer = f.read(1)
            l = buffer[0]
            buffer = f.read(l)
            self.vol_name = buffer[0:l].decode('ascii')
            nxt_toc = 4    # La première TOC débute au bloc 4
            while nxt_toc != 0: # toc = 0 indique la fin du disque (dernière TOC)
                f.seek(nxt_toc * 0x200)  # 0x200 = taille du bloc
                buffer = f.read(2)    # Bloc de la prochaine TOC
                nxt_toc = int.from_bytes(buffer[0:2], 'little') # Sauvegarde début de la TOC suivante
                while True:
                    buffer = f.read(1)
                    if buffer[0] == 0x00:
                        break
                    entree = {'entry_type':buffer[0]}
                    entree['disc'] = disc
                    buffer = f.read(1) # Longueur nom de fichier
                    entree['name_length'] = buffer[0]
                    buffer = f.read(entree['name_length'])
                    entree['file_name'] = buffer[0:entree['name_length']].decode('ascii')
                    buffer = f.read(26)
                    entree['start'] = int.from_bytes(buffer[0:4], 'little')
                    entree['eof'] = int.from_bytes(buffer[4:7], 'little')
                    entree['access'] = buffer[8]
                    entree['file_type'] = buffer[10]
                    entree['aux_type'] = int.from_bytes(buffer[12:14], 'little')
                    entree['storage_type'] = buffer[16]
                    entree['fork'] = buffer[17]
                    bindate = int.from_bytes(buffer[18:20], 'little')
                    entree['cyear2'] = ((bindate & 0b1111111000000000) >> 9)
                    entree['cyear'] = ((bindate & 0b1111111000000000) >> 9) + 1900
                    if entree['cyear'] < 1950:
                        entree['cyear'] += 100
                    entree['cmonth'] = (bindate & 0b0000000111100000) >> 5
                    entree['cday'] = bindate & 0b0000000000011111
                    entree['cmin'] = buffer[20]
                    entree['ch'] = buffer[21]
                    bindate = int.from_bytes(buffer[22:24], 'little')
                    entree['myear2'] = ((bindate & 0b1111111000000000) >> 9)
                    entree['myear'] = ((bindate & 0b1111111000000000) >> 9) + 1900
                    if entree['myear'] < 1950:
                        entree['myear'] += 100
                    entree['mmonth'] = (bindate & 0b0000000111100000) >> 5
                    entree['mday'] = bindate & 0b0000000000011111
                    entree['mmin'] = buffer[24]
                    entree['mh'] = buffer[25]
                    self.toc.append(entree)

    def get_vol_name(self) -> String:
        return self.vol_name
    
    def get_content(self) -> Array:
        return self.toc