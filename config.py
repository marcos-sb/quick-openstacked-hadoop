#!/usr/bin/env/ python

import os, sys, pdb, re


if __name__ == '__main__':
    if os.environ['USER'] == 'root':
        print '*** Please do not run as root...'
        sys.exit(-1)
    cwd = os.getcwd()
    pub = '{home}/Public'.format(home=os.environ['HOME'])
    templates = '{cwd}/Alba/albaproject/mapred/template'.format(cwd=cwd)
    print '\nSetting MEDIA_ROOT to {0}\n'.format(pub)
    print '\nSetting TEMPLATE_DIRS to {0}\n'.format(templates)
    settings_file = '{cwd}/Alba/albaproject/albaproject/settings.py'.format(cwd=cwd)
    new_settings_file = settings_file + '.new'
    with(open(settings_file,'r')) as fin:
        with(open(new_settings_file, 'w')) as fout:
            settings = fin.read()
            settings = re.sub(r'MEDIA_ROOT =.*\n','MEDIA_ROOT = \'{pub}\'\n'.format(pub=pub), settings)
            settings = re.sub(r'TEMPLATE_DIRS =.*\n','TEMPLATE_DIRS = (\'{templates}\')\n'.format(templates=templates), settings)
            fout.write(settings)
    os.rename(new_settings_file, settings_file)            
