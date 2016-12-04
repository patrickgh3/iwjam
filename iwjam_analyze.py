import os
from lxml import etree
import filecmp
import collections
import subprocess

import iwjam_util

ModAnalysisData = collections.namedtuple('ModAnalysisData', ['name', 'dir', 'added', 'removed', 'regrouped', 'modified'])
AddedResource = collections.namedtuple('AddedResource', ['name', 'type', 'restype_group_name', 'group_names', 'elt_text'])
ModifiedResource = collections.namedtuple('ModifiedResource', ['name', 'relpath', 'isbinary', 'difftext'])

def analyze(base_dir, mod_dir):
    base_gmx = iwjam_util.gmx_in_dir(base_dir)
    base_tree = etree.parse(base_gmx)
    base_root = base_tree.getroot()
    mod_gmx = iwjam_util.gmx_in_dir(mod_dir)
    mod_tree = etree.parse(mod_gmx)
    mod_root = mod_tree.getroot()
    mod_name = os.path.split(mod_dir)[1]
    
    analysis_data = ModAnalysisData(name=mod_name, dir=mod_dir, added=[], removed=[], regrouped=[], modified=[])
    
    for mod_restype_elt in iwjam_util.restype_elements_in_tree(mod_tree):
        base_restype_elt = base_root.find(mod_restype_elt.tag)
        recurse_gmx(mod_restype_elt, base_restype_elt, analysis_data)
    added_backup = analysis_data.added
    
    data2 = ModAnalysisData(name='', dir='', added=[], removed=[], regrouped=[], modified=[])
    for base_restype_elt in iwjam_util.restype_elements_in_tree(base_tree):
        mod_restype_elt = mod_root.find(base_restype_elt.tag)
        recurse_gmx(base_restype_elt, mod_restype_elt, data2)
    analysis_data.removed.extend(data2.added)
    
    recurse_files('', base_dir, mod_dir, analysis_data)
    
    return analysis_data

#<assets>
#  <sounds name="sound">
#    <sounds name="sfx">
#      <sound>sound\sndJump</sound>
def recurse_gmx(mod_elt, base_restype_elt, analysis_data):
    groups = [e for e in mod_elt if e.tag == mod_elt.tag]
    leaves = [e for e in mod_elt if not e in groups]
    
    for leaf in leaves:
        resource_name = leaf.text.split('\\')[-1]
        resource_type = leaf.tag
        match_elt = None
        if base_restype_elt != None:
            match_elt = next((e for e in base_restype_elt.findall('.//'+resource_type) if e.text.split('\\')[-1] == resource_name), None) # .// is XPath, recursive
        
        if match_elt == None:
            if '.' in resource_name and resource_name.split('.')[1] in ['gml', 'shader']:
                resource_name = resource_name.split('.')[0]
            analysis_data.added.append(
            AddedResource(name=resource_name, type=resource_type, restype_group_name=mod_elt.tag, group_names=iwjam_util.element_group_names(leaf), elt_text=leaf.text))

        else:
            leaf_groups = iwjam_util.element_group_names(leaf)
            match_groups = iwjam_util.element_group_names(match_elt)
            if leaf_groups != match_groups:
                analysis_data.regrouped.append(
                (resource_name, resource_type, match_groups, leaf_groups))
            
    for group in groups:
        recurse_gmx(group, base_restype_elt, analysis_data)

#project
#  sound
#    sndJump.sound.gmx
#    audio
#      sndJump.wav
def recurse_files(subpath, base_dir, mod_dir, analysis_data):
    subdirs = [e for e in os.scandir(os.path.join(base_dir, subpath)) if e.is_dir() and e.name != 'Configs']
    files = [e for e in os.scandir(os.path.join(base_dir, subpath)) if e.is_file()]
    
    for file in files:
        relpath = os.path.relpath(file.path, base_dir)
        mod_file_path = os.path.join(mod_dir, relpath)
        if not os.path.exists(mod_file_path):
            continue
        
        if not filecmp.cmp(file.path, mod_file_path, shallow=False):
            extension = os.path.splitext(file.path)[1].split('.')[-1]
            if extension in ['gml', 'gmx']:
                difftext = subprocess.run(['diff', '-u', file.path, mod_file_path], stdout=subprocess.PIPE).stdout.decode('utf-8')
                isbinary = False
            else:
                difftext = 'binary file'
                isbinary = True
            analysis_data.modified.append(
            ModifiedResource(name=relpath, relpath=relpath, isbinary=isbinary, difftext=difftext))
    
    for subdir in subdirs:
        relpath = os.path.relpath(subdir.path, base_dir)
        recurse_files(relpath, base_dir, mod_dir, analysis_data)