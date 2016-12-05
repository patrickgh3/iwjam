import os

def gmx_in_dir(dir):
    gmxs = (os.path.join(dir, f) for f in os.listdir(dir)
        if f.endswith('.project.gmx'))
    return next(gmxs, None)

def restype_elements_in_tree(tree):
    return [e for e in tree.getroot()
        if not (e.tag == 'Configs' or e.get('name') is None)]
    
def element_group_names(elt):
    ancestornames = [e.get("name") for e in list(elt.iterancestors())]
    return ancestornames[0:-2][::-1]
