#!/usr/bin/env python3

"""
ProSel-Tools make-image
Makes a ProDOS image from a file hierarchy

2022-05-31 : V0.1   Initial version
"""

import os,glob

__version__ = '0.1'
__author__ = 'Eric Le Bras'

class Image:
    def __init__(self, root_dir) -> None:
        if os.path.exists('dd_32mb.po'):
            os.remove('dd_32mb.po')
        os.system('acx.sh create -d=dd_32mb.po -f=ProDOS_2_4_2.dsk -n=DD -s=32mb --prodos')
        cwd = os.getcwd()
        os.chdir(root_dir)
        files_list = glob.glob('**', recursive=True)
        os.chdir(cwd)
        files_list.sort()
        for file_name in files_list:
            print(file_name)
            if os.path.isdir(root_dir + "/" + file_name):
                os.system('acx.sh md -p -d=dd_32mb.po ' + file_name)
            else:
                dir = os.path.dirname(file_name)
                if dir == "":
                    dir = "/"
                os.system('acx.sh put -f -d=dd_32mb.po --dir=' + dir + ' ' + root_dir + "/" + file_name + ' --applesingle')

if __name__ == '__main__':
    image = Image("./DD")
