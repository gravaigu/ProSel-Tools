#!/usr/bin/env python3

"""
BakkupReport class

2022-05-31 : V0.1   Initial version
"""

__version__ = '0.1'
__author__ = 'Eric Le Bras'

class BakkupReport():
    """
    Generate CVS report for Salvation Bakkup content.
    """

    def __init__(self, fileName):
        self.f = open(fileName, 'w')
        self.f.write(
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

    def __enter__(self):
        return self.f
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.f.close()
    
    def add(self, entree):
        self.f.write(
            '{},{},{},${:08X},{},${:02X},${:02X},${:04X},${:02X},{},{},{},{},{},{},{},{},{},{},{}\n'.format(
                entree['disc'],
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

if __name__ == '__main__':
    # Create empty test report and leave
    with BakkupReport('cvstest.cvs') as my_cvsreport:
        my_cvsreport.add({'disc':'disque 1', 'file_name': 'lklkl'})