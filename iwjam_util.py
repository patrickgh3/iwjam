import os

def gmx_in_dir(dir):
    return next((os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.project.gmx')), None)

def restype_elements_in_tree(tree):
    return [e for e in tree.getroot() if not (e.tag == 'Configs' or e.get('name') is None)]
    
def element_group_names(elt):
    return [e.get("name") for e in list(elt.iterancestors())[0:-2]][::-1]