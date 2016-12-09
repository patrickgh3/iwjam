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
        self.restype = ''
        self.restype_group_name = ''
        self.group_names = ''
        self.elt_text = ''

class ModifiedResource(object):
    def __init__(self):
       self.name = ''
       self.relative_path = ''
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

    # Recurse into restype elements in the mod, paired with
    # restype elements in the base if they exist
    for mod_restype_elt in iwjam_util.restype_elements_in_tree(mod_root):
        base_restype_elt = base_root.find(mod_restype_elt.tag)
        _recurse_gmx(mod_restype_elt, base_restype_elt, pdiff)
    
    # The same as above but reverse the mod and the base, and treat
    # added[] as removed[]
    data2 = ProjectDiff()
    for base_restype_elt in iwjam_util.restype_elements_in_tree(base_root):
        mod_restype_elt = mod_root.find(base_restype_elt.tag)
        _recurse_gmx(base_restype_elt, mod_restype_elt, data2)
    pdiff.removed.extend(data2.added)
    for r in pdiff.removed:
        r.__class__ = RemovedResource
    
    # Recurse into the project directories starting at the root
    _recurse_files('', base_dir, mod_dir, pdiff)
    
    return pdiff

# Fills in added[] and regrouped[] fields of a project diff
# starting at a specific XML element in the mod, and given
# the base resource type element of the base.
def _recurse_gmx(mod_elt, base_restype_elt, pdiff):
    # XML structure:
    # <assets>
    #   <sounds name="sound">
    #     <sounds name="sfx">
    #       <sound>sound\sndJump</sound>

    leaves = [e for e in mod_elt if e.tag != mod_elt.tag]
    groups = [e for e in mod_elt if e.tag == mod_elt.tag]
    
    # Check each leaf if added or regrouped
    for leaf in leaves:
        resource_name = leaf.text.split('\\')[-1]
        resource_type = leaf.tag

        base_matching_leaf = None
        if base_restype_elt != None:
            matches = (e for e in base_restype_elt.findall('.//'+resource_type)
                if e.text.split('\\')[-1] == resource_name)
            base_matching_leaf = next(matches, None)
        
        # If there is no matching leaf in the base, it's an added resource
        if base_matching_leaf == None:
            # Strip extension if .gmx or .shader
            splitname = resource_name.split('.')
            if len(splitname) > 1 and splitname[1] in ['gml', 'shader']:
                resource_name = splitname[0]

            addres = AddedResource()
            addres.name = resource_name
            addres.restype = resource_type
            addres.restype_group_name = mod_elt.tag
            addres.group_names = iwjam_util.element_group_names(leaf)
            addres.elt_text = leaf.text

            pdiff.added.append(addres)

        # If there is a matching leaf in the base, check if regrouped
        else:
            leaf_groups = iwjam_util.element_group_names(leaf)
            match_groups = iwjam_util.element_group_names(base_matching_leaf)
            if leaf_groups != match_groups:
                regres = RegroupedResource()
                regres.name = resource_name

                pdiff.regrouped.append(regres)
    
    # Recurse into groups
    for group in groups:
        _recurse_gmx(group, base_restype_elt, pdiff)

# Fills in modified[] field of a project diff starting at a
# specific subdirectory.
def _recurse_files(relative_path, base_dir, mod_dir, pdiff):
    # Directory structure:
    # project
    #   sound
    #     sndJump.sound.gmx
    #     audio
    #       sndJump.wav

    basedirs = [e for e in os.scandir(os.path.join(base_dir, relative_path))
        if e.is_dir() and e.name != 'Configs']
    basefiles = [e for e in os.scandir(os.path.join(base_dir, relative_path))
        if e.is_file()]
    
    # For each base file, find matching mod file and diff them
    for basefile in basefiles:
        relative_file_path = os.path.relpath(basefile.path, base_dir)
        mod_file_path = os.path.join(mod_dir, relative_file_path)
        # Skip this file if no matching file in the mod
        if not os.path.exists(mod_file_path):
            continue
        
        same = filecmp.cmp(basefile.path, mod_file_path, shallow=False)
        if not same:
            # .gml and .*.gmx files are text
            extension = os.path.splitext(basefile.path)[1].split('.')[-1]
            istext = extension in ['gml', 'gmx']
            if istext:
                isbinary = False
                proc = subprocess.run(
                    ['diff', '-u', basefile.path, mod_file_path],
                    stdout=subprocess.PIPE)
                difftext = proc.stdout.decode('utf-8')
            else:
                isbinary = True
                difftext = 'binary files'

            modres = ModifiedResource()
            modres.name = relative_file_path
            modres.relpath = relative_file_path
            modres.isbinary = isbinary
            modres.difftext = difftext

            pdiff.modified.append(modres)
    
    # Recurse into subdirectories
    for subdir in basedirs:
        relpath = os.path.relpath(subdir.path, base_dir)
        _recurse_files(relpath, base_dir, mod_dir, pdiff)

