"""
Unit and regression test for the mmic_qcschema package.
"""

# Import package, test suite, and other packages as needed
import mmic_qcschema
from mmic_qcschema.components import MolToQCSchemaComponent, QCSchemaToMolComponent
import mmelemental as mmel
import mm_data
import pytest
import sys


try:
    import qcengine
    import psi4
except Exception:
    qcengine = None


mmols = [
    (mmel.models.Molecule(geometry=[0, 0, 0], symbols=["C"])),
    (mmel.models.Molecule.from_file(mm_data.mols["water-mol.json"])),
]


def test_mmic_qcschema_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mmic_qcschema" in sys.modules


@pytest.mark.parametrize("mmol", mmols)
def test_mm_to_qc(mmol):
    inputs = {"schema_object": mmol}
    return MolToQCSchemaComponent.compute(inputs).data_object


def qc_run(qcmol):

    ret = qcengine.compute(
        {
            "molecule": qcmol,
            "driver": "energy",
            "model": {"method": "SCF", "basis": "sto-3g"},
            "keywords": {"scf_type": "df"},
            "extras": {"mtol": 1e-2},
        },
        "psi4",
    )
    return ret


@pytest.mark.parametrize("mmol", mmols)
def test_qc_to_mm(mmol):
    qmol = test_mm_to_qc(mmol)
    if qcengine:
        ret = qc_run(qmol)
        if ret.error:
            raise RuntimeError(ret.error.error_message)
        inputs = {"data_object": ret.molecule}
    else:
        inputs = {"data_object": qmol}
    return QCSchemaToMolComponent.compute(inputs).schema_object
