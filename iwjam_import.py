from lxml import etree
import os
import shutil

import iwjam_util

def do_import(base_dir, mod_dir, analysis):
    base_gmx = iwjam_util.gmx_in_dir(base_dir)
    base_tree = etree.parse(base_gmx)
    base_root = base_tree.getroot()
    mod_gmx = iwjam_util.gmx_in_dir(mod_dir)
    mod_tree = etree.parse(mod_gmx)
    mod_root = mod_tree.getroot()
    
    mod_name = os.path.split(mod_gmx)[1].split('.')[0]
    
    # Add new resources
    for res in analysis.added:
        new_elt = etree.Element(res.type)
        new_elt.text = res.elt_text
        
        group_names = ['stages', analysis.name] + res.group_names
        base_group = base_root.find(res.restype_group_name)
        if base_group is None:
            base_group = etree.SubElement(base_root, res.restype_group_name)
        for g in group_names:
            new_base_group = next((c for c in base_group if c.get('name') == g), None)
            if new_base_group is None:
                new_base_group = etree.SubElement(base_group, base_group.tag)
                new_base_group.set('name', g)
            base_group = new_base_group
        base_group.append(new_elt)
    
    recurse_files('', base_dir, mod_dir, [r.name for r in analysis.added])
    
    base_tree.write(base_gmx, pretty_print=True)
    
    # TODO: Do resource modifications

def recurse_files(subpath, base_dir, mod_dir, res_names):
    subdirs = [e for e in os.scandir(os.path.join(mod_dir, subpath)) if e.is_dir() and e.name != 'Configs']
    files = [e for e in os.scandir(os.path.join(mod_dir, subpath)) if e.is_file()]
    
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
        recurse_files(relpath, base_dir, mod_dir, res_names)

def do_import_old(base_dir, mod_dir, dont_add):
    base_gmx = iwjam_util.gmx_in_dir(base_dir)
    base_tree = etree.parse(base_gmx)
    base_root = base_tree.getroot()
    mod_gmx = iwjam_util.gmx_in_dir(mod_dir)
    mod_tree = etree.parse(mod_gmx)
    mod_root = mod_tree.getroot()
    
    mod_name = os.path.split(mod_gmx)[1].split('.')[0]
    
    added = []
    for mod_restype_elt in iwjam_util.restype_elements_in_tree(mod_tree):
        base_restype_elt = base_root.find(mod_restype_elt.tag)
        if base_restype_elt == None:
            base_restype_elt = etree.SubElement(base_root, mod_restype_elt.tag)
        recurse_gmx(mod_restype_elt, base_restype_elt, mod_name, dont_add, added)
    
    base_tree.write(base_gmx, pretty_print=True)
    
    recurse_files('', base_dir, mod_dir, added)
        
def recurse_gmx(mod_elt, base_restype_elt, mod_name, dont_add, added):
    groups = [e for e in mod_elt if e.tag == mod_elt.tag]
    leaves = [e for e in mod_elt if not e in groups]
    
    for leaf in leaves:
        resource_type = leaf.tag
        resource_name = leaf.text.split('\\')[-1]
        if resource_name in dont_add:
            continue
        
        match_elt = None
        if base_restype_elt != None:
            match_elt = next((e for e in base_restype_elt.findall('.//'+resource_type) if e.text.split('\\')[-1] == resource_name), None) # .// is XPath, recursive
        
        # New resource
        if match_elt == None:
            new_elt = etree.Element(resource_type)
            new_elt.text = leaf.text
            
            group_names = ['stages', mod_name] + iwjam_util.element_group_names(leaf)
            base_group = base_restype_elt
            for g in group_names:
                new_base_group = next((c for c in base_group if c.get('name') == g), None)
                if new_base_group is None:
                    new_base_group = etree.SubElement(base_group, base_group.tag)
                    new_base_group.set('name', g)
                base_group = new_base_group
            base_group.append(new_elt)
            added.append(resource_name)
        
        # Modified resource
        else:
            pass
            
    for group in groups:
        recurse_gmx(group, base_restype_elt, mod_name, dont_add, added)
        