"""
mmic_qcschema
MMSchema to/from QCSchema converter
"""

# Add imports here
from . import components
from . import models

from .mmic_qcschema import molwrite_ext_maps, molread_ext_maps, __version__

_classes_map = {
    "Molecule": models.QCSchemaMol,
}
