#!/usr/bin/env python3

'''salvationtool

Extrait les fichier d'une image disque Salvation

2022-05-24 : V0.1   Version initiale
'''

__version__ = '0.1'
__author__ = 'Eric Le Bras'

import io,os,glob,shutil
from datetime import datetime, timedelta

file_num = 0
len_total = 0

def conv_int16(buffer, pos):
    '''Conversion entier 16 bits'''
    return buffer[pos+1]*2**8 + buffer[pos]

def conv_int24(buffer, pos):
    '''Conversion entier 24 bits'''
    return buffer[pos+2]*2**16 + buffer[pos+1]*2**8 + buffer[pos]

def conv_int32(buffer, pos):
    '''Conversion entier 32 bits'''
    return buffer[pos+3]*2**32 + buffer[pos+2]*2**16 + buffer[pos+1]*2**8 + buffer[pos]

def conv_chaine(buffer, pos, l):
    '''Extrait une chaine de caractères'''
    val = ''
    for i in range(l):
        val += chr(buffer[pos+i])
    return val

def conv_date(date):
    '''Convertit une date en secondes depuis le 1/1/2000'''
    return int((date-datetime(2000,1,1,0,0)).total_seconds()) - 7200

def extend_file(f, offset):
    '''Extends file to offset, filling with zeroes'''
    f.seek(0, io.SEEK_END)
    while f.tell() < offset:
        f.write(b'\x00')

def extend_block(f):
    '''Seek next block begining, filling with zeroes'''
    f.seek(0, io.SEEK_END)
    extend_file(f, f.tell() + 0x200 - f.tell() % 0x200)

def as_file_header(f, entree):
    f.write(b'\x00\x05\x16\x00')  # AppleSingle magic number
    f.write(b'\x00\x02\x00\x00')  # AppleSingle version number
    f.write(b'\x00'*16)
    if entree['storage_type'] == 5:  # Extended file
        f.write((5).to_bytes(2, 'big'))    # 5 entries
    else:
        f.write((4).to_bytes(2, 'big'))    # 4 entries
    f.write((3).to_bytes(4, 'big'))    # Entry type: Real Name
    f.write((0x200).to_bytes(4, 'big'))    # Offset
    f.write(len(os.path.basename(entree['file_name'])).to_bytes(4, 'big'))    # Length
    f.write((8).to_bytes(4, 'big'))    # Entry type: File Dates Info
    f.write((0x400).to_bytes(4, 'big'))    # Offset
    f.write((16).to_bytes(4, 'big'))    # Length
    f.write((11).to_bytes(4, 'big'))    # Entry type: ProDOS File Info
    f.write((0x600).to_bytes(4, 'big'))    # Offset
    f.write((8).to_bytes(4, 'big'))    # Length
    f.write((1).to_bytes(4, 'big'))    # Entry type: Data Fork
    f.write((0x800).to_bytes(4, 'big'))    # Offset
    f.write(entree['eof'].to_bytes(4, 'big'))    # Length
    if entree['storage_type'] == 5:  # Extended file
        f.write((2).to_bytes(4, 'big'))    # Entry type: Data Fork
        f.write((entree['eof'] + 0xa00 - entree['eof'] % 0x200).to_bytes(4, 'big'))    # Offset
        f.write((0).to_bytes(4, 'big'))    # Length
    # 3: Real Name
    extend_file(f, 0x200)
    f.write(bytes(os.path.basename(entree['file_name']), 'ascii'))
    # 8: File Dates Info
    extend_file(f, 0x400)
    f.write(conv_date(datetime(entree['cyear'],
        entree['cmonth'],
        entree['cday'],
        entree['ch'],
        entree['cmin'])).to_bytes(4, 'big', signed=True))
    f.write(conv_date(datetime(entree['myear'],
        entree['mmonth'],
        entree['mday'],
        entree['mh'],
        entree['mmin'])).to_bytes(4, 'big', signed=True))
    f.write(b'\x80\x00\x00\x00')    # Backup date
    f.write(b'\x80\x00\x00\x00')    # Access date
    # 11: ProDOS File Info
    extend_file(f, 0x600)
    f.write(entree['access'].to_bytes(2, 'big'))
    f.write(entree['file_type'].to_bytes(2, 'big'))
    f.write(entree['aux_type'].to_bytes(4, 'big'))
    # 1: Data Fork
    extend_file(f, 0x800)

def extract_toc(toc, vol_root, disc_bu, apple_single):
    global file_num, len_total
    for entree in toc:
        file_name = vol_root + entree['file_name']
        #print('.', end='', flush=True)
        print(file_name)
        if entree['entry_type'] == 0xC0:    # Folder
            os.system('acx.sh md -p -d=dd_32mb.po ' + entree['file_name'])
            #os.makedirs(file_name, exist_ok=True)
            pass
        elif entree['entry_type'] in (0x80, 0x82):  # Fichier normal
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            disc_bu.seek(entree['start'])
            pos = entree['start']
            if os.path.exists(file_name):
                mode = 'r+b'
            else:
                mode = 'wb'
            with open(file_name, mode) as f:
                f.seek(0, io.SEEK_END)
                n = f.tell()
                if apple_single:
                    if f.tell() == 0:
                        as_file_header(f, entree)
                    else:
                        if entree['fork'] == 1:   # Resource fork
                            f.seek(82, io.SEEK_SET)
                            f.write(entree['eof'].to_bytes(4, 'big'))    # Write length
                            #f.seek(78, io.SEEK_SET)
                            #buffer = f.read(4)
                            #extend_file(f, int.from_bytes(buffer, 'big'))
                            f.seek(0, io.SEEK_END)
                            n = 0
                        else:   # File data continuing
                            n -= 0x800
                count = 0
                while n < entree['eof'] and (entree['entry_type'] != 0x82 or pos < 0xb4000):
                    buffer = disc_bu.read(1)
                    pos += 1
                    if count > 0:
                        f.write(buffer)
                        n += 1
                        count -= 1
                        continue
                    if buffer[0] > 0xBF:    # n fois $00
                        nbr = buffer[0] - 0xBD
                        for i in range(nbr):
                            f.write(b'\x00')
                        n += nbr
                        continue
                    if buffer[0] > 0x7F:    # n fois l'octet suivant
                        nbr = buffer[0] - 0x7D
                        buffer = disc_bu.read(1)
                        pos += 1
                        for i in range(nbr):
                            f.write(buffer)
                        n += nbr
                        continue
                    if buffer[0] > 0x3F:     # n octets
                        count = buffer[0] - 0x3F
                        continue
                    if buffer[0] == 0:      # $4000 octets
                        count = 0x4000
                        continue
                    print('!', end='')
                if entree['entry_type'] == 0x80:
                    extend_block(f)
            len_total += n
            file_num += 1
            if entree['entry_type'] == 0x80 and (entree['storage_type'] != 5 or entree['fork'] == 1):
                dir = os.path.dirname(entree['file_name'])
                if dir == "":
                    dir = "/"
                os.system('acx.sh put -f -d=dd_32mb.po --dir=' + dir + ' ' + file_name + ' --applesingle')
        else:
            print('?', end='', flush=True)

def main():
    extract = True
    printcvs = True
    outputfile = 'archivelist.cvs'
    discs = glob.glob('salvation_backup/salvation_*.po')
    discs.sort()
    disc_num = 0
    if printcvs:
        try:
            outputfileh = open(outputfile, 'w')
            outputfileh.write(
                '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                    'disc',
                    'name_length',
                    'file_name',
                    'start',
                    'eof',
                    'access',
                    'file_type',
                    'aux_type',
                    'storage_type',
                    'fork',
                    'cyear',
                    'cmonth',
                    'cday',
                    'cmin',
                    'ch',
                    'myear',
                    'mmonth',
                    'mday',
                    'mmin',
                    'mh'))
        except IOError:
            print('Ne peux pas créer le fichier', outputfile)
            exit(2)
    for disc in discs:
        with open(disc, 'rb') as disc_bu:
            disc_num += 1
            if disc_num == 1:
                disc_bu.seek(0x200)
                buffer = disc_bu.read(1)
                l = buffer[0]
                buffer = disc_bu.read(l)
                vol_root = '.' + conv_chaine(buffer, 0, l)
                if extract:
                    shutil.rmtree(vol_root, ignore_errors=True)
                    if os.path.exists('dd_32mb.po'):
                        os.remove('dd_32mb.po')
                    os.system('acx.sh create -d=dd_32mb.po -f=ProDOS_2_4_2.dsk -n=DD -s=32mb --prodos')
                    os.system('acx.sh md -p -d=dd_32mb.po SYSTEM')
                    os.system('acx.sh md -p -d=dd_32mb.po ICONS')
                    os.system('acx.sh md -p -d=dd_32mb.po UTIL')
                    os.system('acx.sh md -p -d=dd_32mb.po ORCA')
            nxt_toc = 4    # La première TOC débute au bloc 4
            while nxt_toc != 0: # toc = 0 indique la fin du disque (dernière TOC)
                toc = []
                disc_bu.seek(nxt_toc * 0x200)  # 0x200 = taille du bloc
                buffer = disc_bu.read(2)    # Bloc de la prochaine TOC
                nxt_toc = conv_int16(buffer, 0) # Sauvegarde début de la TOC suivante
                while True:
                    buffer = disc_bu.read(1)
                    entree = {'entry_type':buffer[0]}
                    if buffer[0] == 0x00:
                        break
                    buffer = disc_bu.read(1) # Longueur nom de fichier
                    entree['name_length'] = buffer[0]
                    buffer = disc_bu.read(entree['name_length'])
                    entree['file_name'] = conv_chaine(buffer, 0, entree['name_length'])
                    buffer = disc_bu.read(26)
                    entree['start'] = conv_int32(buffer, 0)
                    entree['eof'] = conv_int24(buffer, 4)
                    entree['access'] = buffer[8]
                    entree['file_type'] = buffer[10]
                    entree['aux_type'] = conv_int16(buffer, 12)
                    entree['storage_type'] = buffer[16]
                    entree['fork'] = buffer[17]
                    bindate = conv_int16(buffer, 18)
                    entree['cyear'] = ((bindate & 0b1111111000000000) >> 9) + 1900
                    if entree['cyear'] < 1950:
                        entree['cyear'] += 100
                    entree['cmonth'] = (bindate & 0b0000000111100000) >> 5
                    entree['cday'] = bindate & 0b0000000000011111
                    entree['cmin'] = buffer[20]
                    entree['ch'] = buffer[21]
                    bindate = conv_int16(buffer, 22)
                    entree['myear'] = ((bindate & 0b1111111000000000) >> 9) + 1900
                    if entree['myear'] < 1950:
                        entree['myear'] += 100
                    entree['mmonth'] = (bindate & 0b0000000111100000) >> 5
                    entree['mday'] = bindate & 0b0000000000011111
                    entree['mmin'] = buffer[24]
                    entree['mh'] = buffer[25]
                    if printcvs:
                        outputfileh.write(
                            '{},{},{},${:08X},{},${:02X},${:02X},${:04X},${:02X},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                                disc,
                                entree['name_length'],
                                entree['file_name'],
                                entree['start'],
                                entree['eof'],
                                entree['access'],
                                entree['file_type'],
                                entree['aux_type'],
                                entree['storage_type'],
                                entree['fork'],
                                entree['cyear'],
                                entree['cmonth'],
                                entree['cday'],
                                entree['cmin'],
                                entree['ch'],
                                entree['myear'],
                                entree['mmonth'],
                                entree['mday'],
                                entree['mmin'],
                                entree['mh']))
                    toc.append(entree)
                if extract:
                    extract_toc(toc, vol_root, disc_bu, True)
    if extract:
        print("\nNb d'images disque traitées =", disc_num)
        print("Nb de fichiers extraits =", file_num)
        print("Nb d'octets écrits =", len_total)
        print("Extraction terminée")
    if printcvs:
        outputfileh.close()

if __name__ == '__main__':
   main()