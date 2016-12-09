import os
import shutil
import signal
import sys
import iwjam_diff
import iwjam_analyze
import iwjam_import
import iwjam_util

def main():
    base_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/base'
    mods_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/mods'
    mod_dirs = [e.path for e in os.scandir(mods_dir)
        if e.is_dir() and not iwjam_util.gmx_in_dir(e.path) is None]
    
    pdiffs = []
    for md in mod_dirs:
        pdiff = iwjam_diff.compute_diff(base_dir, md)
        pdiffs.append(pdiff)
        print('{:<15} {:<3} added, {:<2} modified, '
            '{:<2} regrouped, {:<2} removed'.format(
            pdiff.mod_name,
            len(pdiff.added),
            len(pdiff.modified),
            len(pdiff.regrouped),
            len(pdiff.removed)))

    collisions = iwjam_analyze.collisions_in_diffs(pdiffs)
    print('{} added collisions'.format(len(collisions.added)))
    for c in collisions.added:
        modnames = (d.mod_name for (d,res) in c.present_in if res.isbinary)
        print('{}: {}'.format(c.resourcename, ', '.join(modnames)))

    print('{} modified collisions'.format(len(collisions.modified)))
    for c in collisions.modified:
        modnames = (d.mod_name for (d,res) in c.present_in if res.isbinary)
        print('{}: {}'.format(c.resourcename, ', '.join(modnames)))

    for ai, analysis in enumerate(pdiffs):
        continue
        print('\n\n{} {}\n\n'.format(ai, analysis.mod_name))
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
        
    if len(collisions.added) != 0:
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
    for pdiff in pdiffs:
        iwjam_import.do_import(base_dir=comp_dir,
            mod_dir=pdiff.mod_dir,
            analysis=pdiff)
        print('{}: done'.format(analysis.mod_name))

def signal_handler(signal, frame):
    print('Stopped.')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    main()

