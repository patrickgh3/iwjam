import os
from lxml import etree
import filecmp
import subprocess
import iwjam_util

# Data structures used for passing around the analysis results.
class ProjectDiff(object):
    def __init__(self):
        self.base_name = ''
        self.base_dir = ''
        self.mod_name = ''
        self.mod_dir = ''
        self.added = []
        self.removed = []
        self.regrouped = []
        self.modified = []

class AddedResource(object):
    def __init__(self):
        self.name = ''
        self.type = ''
        self.restype_group_name = ''
        self.group_names = ''
        self.elt_text = ''

class ModifiedResource(object):
    def __init__(self):
       self.name = ''
       self.relpath = ''
       self.isbinary = False
       self.difftext = ''

class RemovedResource(AddedResource):
    pass

class RegroupedResource(AddedResource):
    pass

# compute_diff(base_dir, mod_dir)
# Returns a ProjectDiff namedtuple (defined above) which represents the
# diff between two projects.
def compute_diff(base_dir, mod_dir):
    pdiff = ProjectDiff()
    pdiff.base_dir = base_dir
    pdiff.base_name = os.path.split(base_dir)[1]
    pdiff.mod_dir = mod_dir
    pdiff.mod_name = os.path.split(mod_dir)[1]

    base_gmx = iwjam_util.gmx_in_dir(base_dir)
    base_tree = etree.parse(base_gmx)
    base_root = base_tree.getroot()
    mod_gmx = iwjam_util.gmx_in_dir(mod_dir)
    mod_tree = etree.parse(mod_gmx)
    mod_root = mod_tree.getroot()

    for mod_restype_elt in iwjam_util.restype_elements_in_tree(mod_root):
        base_restype_elt = base_root.find(mod_restype_elt.tag)
        _recurse_gmx(mod_restype_elt, base_restype_elt, pdiff)
    
    data2 = ProjectDiff()
    for base_restype_elt in iwjam_util.restype_elements_in_tree(base_root):
        mod_restype_elt = mod_root.find(base_restype_elt.tag)
        _recurse_gmx(base_restype_elt, mod_restype_elt, data2)
    pdiff.removed.extend(data2.added)
    for r in pdiff.removed:
        r.__class__ = RemovedResource
    
    _recurse_files('', base_dir, mod_dir, pdiff)
    
    return pdiff

def _recurse_gmx(mod_elt, base_restype_elt, pdiff):
    #<assets>
    #  <sounds name="sound">
    #    <sounds name="sfx">
    #      <sound>sound\sndJump</sound>

    groups = [e for e in mod_elt if e.tag == mod_elt.tag]
    leaves = [e for e in mod_elt if not e in groups]
    
    for leaf in leaves:
        resource_name = leaf.text.split('\\')[-1]
        resource_type = leaf.tag
        match_elt = None
        if base_restype_elt != None:
            matches = (e for e in base_restype_elt.findall('.//'+resource_type)
                if e.text.split('\\')[-1] == resource_name)
            match_elt = next(matches, None)
        
        if match_elt == None:
            # Strip extension if .gmx or .shader
            splitname = resource_name.split('.')
            if len(splitname) > 1 and splitname[1] in ['gml', 'shader']:
                resource_name = splitname[0]

            addres = AddedResource()
            addres.name = resource_name
            addres.type = resource_type
            addres.restype_group_name = mod_elt.tag
            addres.group_names = iwjam_util.element_group_names(leaf)
            addres.elt_text = leaf.text
            pdiff.added.append(addres)

        else:
            leaf_groups = iwjam_util.element_group_names(leaf)
            match_groups = iwjam_util.element_group_names(match_elt)
            if leaf_groups != match_groups:
                regres = RegroupedResource()
                regres.name = resource_name
                
                pdiff.regrouped.append(regres)
                    #(resource_name, resource_type, match_groups, leaf_groups))
            
    for group in groups:
        _recurse_gmx(group, base_restype_elt, pdiff)

def _recurse_files(subpath, base_dir, mod_dir, pdiff):
    #project
    #  sound
    #    sndJump.sound.gmx
    #    audio
    #      sndJump.wav

    subdirs = [e for e in os.scandir(os.path.join(base_dir, subpath))
        if e.is_dir() and e.name != 'Configs']
    files = [e for e in os.scandir(os.path.join(base_dir, subpath))
        if e.is_file()]
    
    for file in files:
        relpath = os.path.relpath(file.path, base_dir)
        mod_file_path = os.path.join(mod_dir, relpath)
        if not os.path.exists(mod_file_path):
            continue
        
        if not filecmp.cmp(file.path, mod_file_path, shallow=False):
            extension = os.path.splitext(file.path)[1].split('.')[-1]
            if extension in ['gml', 'gmx']:
                proc = subprocess.run(
                    ['diff', '-u', file.path, mod_file_path],
                    stdout=subprocess.PIPE)
                difftext = proc.stdout.decode('utf-8')
                isbinary = False
            else:
                difftext = 'binary file'
                isbinary = True
            modres = ModifiedResource()
            modres.name = relpath
            modres.relpath = relpath
            modres.isbinary = isbinary
            modres.difftext = difftext
            pdiff.modified.append(modres)
    
    for subdir in subdirs:
        relpath = os.path.relpath(subdir.path, base_dir)
        _recurse_files(relpath, base_dir, mod_dir, pdiff)

