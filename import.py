import argparse
import iwjam_diff
import iwjam_import
import os
import shutil
import iwjam_util

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('basedir')
    parser.add_argument('moddir')
    parser.add_argument('enginedir')
    parser.add_argument('folder')
    args = parser.parse_args()

    project_diff = iwjam_diff.compute_diff(base_dir=args.enginedir,
            mod_dir=args.moddir)

    print('{} Modified'.format(len(project_diff.modified)))
    for m in project_diff.modified:
        print('    '+m.name)
        if m.isbinary or '.room.gmx' in m.name:
            pass
        else:
            for line in m.difftext.replace('\r', '').split('\n')[2:]:
                if line != '':
                    print('            '+str(line.encode('utf-8'))[2:-1])

    i = input('Proceed with import? (y/n) ')
    if i != 'y':
        print('Aborted')
        return

    project_diff = iwjam_diff.compute_diff(base_dir=args.basedir,
            mod_dir=args.moddir)

    iwjam_import.do_import(base_dir=args.basedir, mod_dir=args.moddir,
            pdiff=project_diff, folder_prefixes=args.folder.split('/'))
    print('Done')

if __name__ == '__main__':
    main()
