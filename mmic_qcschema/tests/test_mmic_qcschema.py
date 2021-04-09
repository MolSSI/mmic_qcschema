"""
Unit and regression test for the mmic_qcschema package.
"""

# Import package, test suite, and other packages as needed
import mmic_qcschema
import pytest
import sys

def test_mmic_qcschema_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "mmic_qcschema" in sys.modules
