import collections

# Data structures used for passing around the analysis results.
class ProjectDiffsCollisions:
    def __init__(self):
        # Lists of ResourceCollisions
        self.added = []
        self.modified = []
        self.removed = []
        self.regrouped = []

class ResourceCollision:
    def __init__(self):
        self.resourcename = ''
        self.present_in = [] # List of tuples of (diff, resource)

# Given a list of project diffs, returns a ProjectDiffsCollisions object
# that represents resources added, modified, removed, or regrouped
# in more than 1 project diff.
def collisions_in_diffs(pdiffs):
    collisions = ProjectDiffsCollisions()
    collisions.added = collisions_in_diffs_one_list(
        pdiffs, lambda x: x.added)
    collisions.modified = collisions_in_diffs_one_list(
        pdiffs, lambda x: x.modified)
    collisions.removed = collisions_in_diffs_one_list(
        pdiffs, lambda x: x.removed)
    collisions.regrouped = collisions_in_diffs_one_list(
        pdiffs, lambda x: x.regrouped)

    return collisions

# Called from collisions_in_diffs.
# Given a list of project diffs and a function that given a diff
# returns which resource list you're interested in (added, modified, etc),
# returns a list of ResourceCollisions representing resources that are
# present in more than 1 project diff.
def collisions_in_diffs_one_list(pdiffs, list_from_diff):
    present_in = collections.defaultdict(list)
    for pdiff in pdiffs:
        for res in list_from_diff(pdiff):
            present_in[res.name].append((pdiff, res))

    rescollisions = []
    for resname, diffs_resources in present_in.items():
        if len(diffs_resources) > 1:
            rc = ResourceCollision()
            rc.resourcename = resname
            rc.present_in = diffs_resources
            rescollisions.append(rc)

    return sorted(rescollisions, key=lambda x: x.resourcename)

