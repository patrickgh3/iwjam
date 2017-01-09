from lxml import etree
import os
import shutil
import iwjam_util

# Performs an import of a mod project into a base project given a
# previously computed ProjectDiff between them,
# and a list of folder names to prefix
# ('%modname%' will be replaced with the mod's name)
def do_import(base_dir, mod_dir, pdiff, folder_prefixes=['%modname%']):
    # Replace %modname%
    for i, p in enumerate(folder_prefixes):
        if p == '%modname%':
            folder_prefixes[i] = pdiff.mod_name

    # Set up XML
    base_gmx = iwjam_util.gmx_in_dir(base_dir)
    base_tree = etree.parse(base_gmx)
    base_root = base_tree.getroot()

    mod_gmx = iwjam_util.gmx_in_dir(mod_dir)
    mod_tree = etree.parse(mod_gmx)
    mod_root = mod_tree.getroot()

    # For each added resource
    for addedres in pdiff.added:
        # Create a new resource element
        new_elt = etree.Element(addedres.restype)
        new_elt.text = addedres.elt_text

        # Create list of names of groups to traverse/create 
        group_names = folder_prefixes + addedres.group_names
        baseElt = base_root.find(addedres.restype_group_name)
        # Create resource type element if it doesn't exist
        if baseElt is None:
            baseElt = etree.SubElement(base_root, addedres.restype_group_name)

        # Traverse groups, creating nonexistent ones along the way
        for g in group_names:
            # Try to find group element with the current name
            nextBaseElt = next(
                    (c for c in baseElt if c.get('name') == g), None)
            # Create group element if it doesn't exist
            if nextBaseElt is None:
                nextBaseElt = etree.SubElement(baseElt, baseElt.tag)
                nextBaseElt.set('name', g)
            baseElt = nextBaseElt
        
        # Add the new resource element
        baseElt.append(new_elt)
    
    # Write project file
    base_tree.write(base_gmx, pretty_print=True)

    # Now, copy the files
    _recurse_files('', base_dir, mod_dir, [r.name for r in pdiff.added])
    
    # TODO: Modified resources

def _recurse_files(subpath, base_dir, mod_dir, res_names):
    subdirs = [e for e in os.scandir(os.path.join(mod_dir, subpath))
        if e.is_dir() and e.name != 'Configs']
    files = [e for e in os.scandir(os.path.join(mod_dir, subpath))
        if e.is_file()]
    
    for file in files:
        resname = file.name.split('.')[0]
        extension = file.name.split('.')[-1]
        if subpath.split('\\')[0] == 'sprites' and extension == 'png':
            resname = '_'.join(resname.split('_')[0:-1])
        
        if resname in res_names:
            relpath = os.path.relpath(file.path, mod_dir)
            base_file_path = os.path.join(base_dir, relpath)
            shutil.copyfile(file.path, base_file_path)
    
    for subdir in subdirs:
        relpath = os.path.relpath(subdir.path, mod_dir)
        base_path = os.path.join(base_dir, relpath)
        if not os.path.exists(base_path):
            os.mkdir(base_path)
        _recurse_files(relpath, base_dir, mod_dir, res_names)
       
