import os

def gmx_in_dir(dir):
    gmxs = (os.path.join(dir, f) for f in os.listdir(dir)
        if f.endswith('.project.gmx'))
    return next(gmxs, None)

def restype_elements_in_tree(root):
    # Any top-level element without a name is not a resource type,
    # and any one with a name (that isn't Configs) is a resource type.
    return [e for e in root
        if not e.get('name') is None and e.tag != 'Configs']
    
def element_group_names(elt):
    ancestornames = [e.get("name") for e in list(elt.iterancestors())]
    return ancestornames[0:-2][::-1]
