# An example usage of analysis and importing done for I Wanna Spook Jam

import os
import shutil
import sys
import iwjam_diff
import iwjam_analyze
import iwjam_import
import iwjam_util

# Define base and mods location
base_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/base'
mods_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/mods'
mod_dirs = [e.path for e in os.scandir(mods_dir)
    if e.is_dir() and not iwjam_util.gmx_in_dir(e.path) is None]

# Diff the base against each mod
print('Starting diffs')
pdiffs = []
for md in mod_dirs:
    print('{:<15}'.format(os.path.split(md)[1]+'...'), end='')
    sys.stdout.flush()
    pdiff = iwjam_diff.compute_diff(base_dir, md)
    pdiffs.append(pdiff)
    # Print overview of each diff as we go
    print(' {:<3} added, {:<2} modified, '
        '{:<2} regrouped, {:<2} removed'.format(
        len(pdiff.added),
        len(pdiff.modified),
        len(pdiff.regrouped),
        len(pdiff.removed)))

# Find collisions
collisions = iwjam_analyze.collisions_in_diffs(pdiffs)

# Print collisions
print('{} added collisions'.format(len(collisions.added)))
for c in collisions.added:
    modnames = (d.mod_name for (d,res) in c.present_in)
    print('    {}: {}'.format(c.resourcename, ', '.join(modnames)))
print('{} modified collisions'.format(len(collisions.modified)))
for c in collisions.modified:
    modnames = (d.mod_name for (d,res) in c.present_in if res.isbinary)
    print('    {}: {}'.format(c.resourcename, ', '.join(modnames)))

# Print diff texts of all modified resources
#print('Modified diffs')
for i, analysis in enumerate(pdiffs):
    continue # disable this for now

    print('\n\n{} {}\n\n'.format(i, analysis.mod_name))
    for res in analysis.modified:
        # Ignore certain resource names we aren't interested in
        if res.name in ['rooms\\rGraphicsTest.room.gmx',
                        'rooms\\rTemplate.room.gmx',
                        'scripts\\scrSetGlobalOptions.gml']:
            continue

        print('\nRESOURCE\n{}'.format(res.name))
        
        # Special cases, don't print diff text
        if res.isbinary:
            print('    binary diff')
            continue 
        if '.room.gmx' in res.name:
            print('    room diff')
            continue

        # Print diff text with different formatting
        for line in res.difftext.replace('\r', '').split('\n')[2:]:
            if line != '':
                if line[0] == '+':
                    line = line[1:]
                elif line[0] == ' ':
                    line = '>'+line[1:]
            print(line)

# Probably shouldn't do import if haven't manually resolved add collisions
if len(collisions.added) != 0:
    print('WARNING! There are still add collisions')

# Clone base project into output directory
out_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/output'
if os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
print('Copying to out dir')
shutil.copytree(base_dir, out_dir)
os.rename(iwjam_util.gmx_in_dir(out_dir),
        os.path.join(out_dir, 'output.project.gmx'))

# Import all mods into output project
print('Starting import')
for pdiff in pdiffs:
    print('{}...'.format(pdiff.mod_name), end='')
    sys.stdout.flush()
    iwjam_import.do_import(out_dir, pdiff.mod_dir, pdiff)
    print('done')

