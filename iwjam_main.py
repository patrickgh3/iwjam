# Analyzes and imports between a base GM project and a group of mod projects.

import os
import shutil
import collections
import pickle
import signal
import sys

import iwjam_analyze
import iwjam_import
import iwjam_util

def main():
    base_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/base'
    
    mods_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/mods'
    mod_dirs = [e.path for e in os.scandir(mods_dir)
        if e.is_dir() and not iwjam_util.gmx_in_dir(e.path) is None]
    
    print('Starting analysis')
    analyses = []
    for md in mod_dirs:
        analysis_data = iwjam_analyze.compute_diff(base_dir, md)
        analyses.append(analysis_data)
        #print()
        print('{:<15} {:<3} added, {:<2} modified,\
            {:<2} regrouped, {:<2} removed'.format(
            analysis_data.name,
            len(analysis_data.added),
            len(analysis_data.modified),
            len(analysis_data.regrouped),
            len(analysis_data.removed)))
        #print('Binary: ')
        #for m in [m for m in analysis_data.modified if m.isbinary]:
        #    print(m.name)
        #print('Not binary:')
        #for m in [m for m in analysis_data.modified if not m.isbinary]:
        #    print(m.name)
            #print(m.difftext)
    
    print('')
    a = [(m.name, m.added) for m in analyses]
    added_collisions = find_collisions(a)
    print('{} added collisions'.format(len(added_collisions)))
    for c in added_collisions:
        print('{}: {}'.format(c[0], ', '.join(c[1])))
    
    m = [(m.name, m.modified) for m in analyses]
    modified_collisions = find_collisions(m)
    print('{} modified collisions'.format(len(modified_collisions)))
    print('Binary:')
    for c in [c for c in modified_collisions if c[1][0][1].isbinary]:
        print('{}: {}'.format(c[0], ', '.join([a[0] for a in c[1]])))
    print('Not binary:')
    for c in [c for c in modified_collisions if not c[1][0][1].isbinary]:
        print('{}: {}'.format(c[0], ', '.join([a[0] for a in c[1]])))

    for ai, analysis in enumerate(analyses):
        print('\n\n{} {}\n\n'.format(ai, analysis.name))
        for res in analysis.modified:
            if res.name in ['rooms\\rGraphicsTest.room.gmx',
                            'rooms\\rTemplate.room.gmx',
                            'scripts\\scrSetGlobalOptions.gml']:
                continue
            if res.isbinary:
                continue
                
            print('\nRESOURCE\n'+res.name)
            
            if '.room.gmx' in res.name:
                print('    room diff')
                continue
            for line in res.difftext.replace('\r', '').split('\n')[2:]:
                if line != '':
                    if line[0] == '+':
                        line = line[1:]
                    elif line[0] == ' ':
                        line = '>'+line[1:]
                print(line)
        
    if len(added_collisions) != 0:
        print('Can\'t do imports when there are add collisions.')
        exit()
    
    comp_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/output'
    if os.path.isdir(comp_dir):
        print('Removing comp dir')
        shutil.rmtree(comp_dir)
    print('Copying to comp dir')
    shutil.copytree('C:/Patrick/Projects/Python/iwjam/spook jam testing/base',
        comp_dir)
    os.rename(iwjam_util.gmx_in_dir(comp_dir),
        os.path.join(comp_dir, 'output.project.gmx'))
    
    print('\nStarting import\n')
    for analysis in analyses:
        iwjam_import.do_import(base_dir=comp_dir,
            mod_dir=analysis.dir,
            analysis=analysis)
        print('{}: done'.format(analysis.name))

def find_collisions(mods_resources):
    res_users = {}
    for modname, reslist in mods_resources:
        for r in reslist:
            if not r.name in res_users:
                res_users[r.name] = []
            res_users[r.name].append((modname, r))
    collisions = [a for a in res_users.items() if len(a[1]) > 1]
    return sorted(collisions, key=lambda x: x[0])

def signal_handler(signal, frame):
    print('Stopped.')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()

