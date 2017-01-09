iwjam (I Wanna Jam)
---

Automates diffing and importing resources between two GameMaker projects. Used in I Wanna Spook Jam and I Wanna Try a Collab 2, where many people worked independently off of the same base project, and their new content was imported back into that project. Based on [Klazen's original script](https://github.com/Klazen108/gm_resource_import).

Features:

Compute diff of two projects, in terms of added, modified, regrouped, and deleted resources, and their details.

Find collisions among multiple project diffs. (e.g. resources added, modified, regrouped, or deleted in more than one project diff)

Perform import of new resources from one project into another, adding optional top-level folders to keep things organized.

See example_usage.py for how this was used in I Wanna Spook Jam.

