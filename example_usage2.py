import os
import shutil
import sys
import iwjam_diff
import iwjam_analyze
import iwjam_import
import iwjam_util

base_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/base'
mod_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/mods/Klazen'
out_dir = 'C:/Patrick/Projects/Python/iwjam/spook jam testing/output'

# Compute diff
pdiff = iwjam_diff.compute_diff(base_dir=base_dir, mod_dir=mod_dir)
print(' {:<3} added, {:<2} modified, '
        '{:<2} regrouped, {:<2} removed'.format(
        len(pdiff.added),
        len(pdiff.modified),
        len(pdiff.regrouped),
        len(pdiff.removed)))

# Print modifications
for res in pdiff.modified:
    # Ignore certain resource names we aren't interested in
    #if res.name in ['rooms\\rGraphicsTest.room.gmx',
    #                'rooms\\rTemplate.room.gmx',
    #                'scripts\\scrSetGlobalOptions.gml']:
    #    continue

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

# Clone base project into output directory
if os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
print('Copying to out dir')
shutil.copytree(base_dir, out_dir)
os.rename(iwjam_util.gmx_in_dir(out_dir),
        os.path.join(out_dir, 'output.project.gmx'))

# Import
iwjam_import.do_import(out_dir, mod_dir, pdiff)
