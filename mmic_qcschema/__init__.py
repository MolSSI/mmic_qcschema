"""
mmic_qcschema
MMSchema to/from QCSchema converter
"""

# Add imports here
from . import components
from . import models

# Handle versioneer
from ._version import get_versions

versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions


molread_ext_maps = {
    ".xyz": "xyz",
    ".json": "json",
    ".msgpack": "msgpack",
}

molwrite_ext_maps = {".xyz": "xyz", ".json": "json", ".msgpack": "msgpack"}

_classes_map = {
    "Molecule": models.QCSchemaMol,
}
