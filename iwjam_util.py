import os

# Returns the path of a .project.gmx file in a directory,
# or None if none exist
def gmx_in_dir(dir):
    gmxs = (os.path.join(dir, f) for f in os.listdir(dir)
        if f.endswith('.project.gmx'))
    return next(gmxs, None)

# Returns children of an etree elt that are valid GameMaker resource type elts
# All are valid except those without a name and the one named 'Configs'
def restype_elements_in_tree(root):
    return [e for e in root
        if not e.get('name') is None and e.tag != 'Configs']

# Returns a list of group names of a resource element,
# i.e. all except the first two which are the root and the restype element
def element_group_names(elt):
    ancestornames = [e.get("name") for e in list(elt.iterancestors())]
    return ancestornames[0:-2][::-1]
