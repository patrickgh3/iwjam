import os, shutil, sys
import argparse
import iwjam_diff, iwjam_analyze, iwjam_import, iwjam_util

def main():
    # Command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('stage_dir', help='The stage to import.')
    parser.add_argument('compilation_dir', help='The project to import the '
        'stage into.')
    #parser.add_argument('engine_dir', help='The base engine project the stage'
    #    'started with, used for diagonstic purposes.')
    parser.add_argument('gm_subfolders', help='Slash-separated list of folders '
        'that will be created in GameMaker. (e.g. "Stages/Piece")')
    args = parser.parse_args()



    # Diff the stage and the compilation.

    diff = iwjam_diff.compute_diff(
        base_dir=args.compilation_dir,
        mod_dir=args.stage_dir
    )

    print('{} new resources'.format(len(diff.added)))
    for r in diff.added:
        print(r.name)
    print('')

    print('{} different resources'.format(len(diff.modified)))
    for r in diff.modified:
        print(r.name)
    print('')



    print('Proceed with import into {}? Be sure you\'ve backed up that '
        'project.\n(y/n) '.format(args.compilation_dir), end='')
    if input() != 'y':
        print('Aborted')
        return

    # Import the stage into the compilation.

    iwjam_import.do_import(
        base_dir=args.compilation_dir,
        mod_dir=args.stage_dir,
        pdiff=diff,
        folder_prefixes=args.gm_subfolders.split('/')
    )

    print('Done')

if __name__ == '__main__':
    main()
