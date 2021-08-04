from typing import Dict, Any, Optional
from mmic_translator.models.base import ToolkitModel
from mmelemental.models.molecule import Molecule
import qcelemental

# QCElemental converter components
from mmic_qcschema.components.mol_component import (
    QCSchemaToMolComponent,
    MolToQCSchemaComponent,
)

__all__ = ["QCSchemaMol"]


class QCSchemaMol(ToolkitModel):
    """A model for QCSchema storing an equivalent MMSchema molecule."""

    @classmethod
    def engine(cls):
        return "qcelemental", qcelemental.__version__

    @classmethod
    def dtype(cls):
        """Returns the fundamental molecule object type."""
        return qcelemental.models.Molecule

    @classmethod
    def isvalid(cls, data):
        """Makes sure the Structure object stores atoms."""
        if hasattr(data, "symbols"):
            if len(data.symbols):
                return data

        raise AttributeError("QCSchema molecule object does not store any atoms!")

    @classmethod
    def from_file(
        cls,
        filename: str,
        top_filename: Optional[str] = None,
        dtype: Optional[str] = None,
        **kwargs
    ) -> "QCSchemaMol":
        """
        Constructs an QCSchemaMol object from file(s).

        Parameters
        ----------
        filename : str
            The molecule geometry filename to read
        top_filename: str, optional
            The topology i.e. connectivity filename to read
        **kwargs
            Any additional keywords to pass to the constructor
        Returns
        -------
        qcelemental.models.Molecule
            A constructed QCSchema molecule object.
        """
        if top_filename:
            raise NotImplementedError(
                "Topology/connectivity files not supported in QCElemental."
            )
        mol = qcelemental.models.Molecule.from_file(filename, dtype, **kwargs)
        return cls(data=mol)

    @classmethod
    def from_schema(
        cls, data: Molecule, version: Optional[int] = None, **kwargs: Dict[str, Any]
    ) -> "QCSchemaMol":
        """
        Constructs a QCSchema Molecule object from an MMSchema Molecule object.
        Parameters
        ----------
        data: Molecule
            Data to construct Molecule from.
        version: int, optional
            Schema version e.g. 1. Overrides data.schema_version.
        **kwargs
            Additional kwargs to pass to the constructors.
        Returns
        -------
        QCSchemaMol
            A constructed QCSchema Molecule object.
        """
        inputs = {
            "schema_object": data,
            "schema_version": version or data.schema_version,
            "schema_name": kwargs.pop("schema_name", data.schema_name),
            "keywords": kwargs,
        }
        out = MolToQCSchemaComponent.compute(inputs)
        return cls(data=out.data_object, units=out.data_units)

    def to_file(self, filename: str, dtype: str = None, mode: str = None, **kwargs):
        """Writes the molecule to a file.
        Parameters
        ----------
        filename : str
            The filename to write to
        dtype : Optional[str], optional
            File format
        **kwargs
            Additional kwargs to pass to the constructors. kwargs takes precedence over  data.
        """
        if mode:
            raise NotImplementedError("File write mode not supported in QCElemental.")

        self.data.to_file(filename, dtype, **kwargs)

    def to_schema(self, version: Optional[int] = 0, **kwargs) -> Molecule:
        """Converts the molecule to MMSchema molecule.
        Parameters
        ----------
        version: str, optional
            Schema specification version to comply with e.g. 1
        **kwargs
            Additional kwargs to pass to the constructor.
        """
        inputs = {
            "data_object": self.data,
            "schema_version": version,
            "schema_name": "mmschema_molecule",
            "keywords": kwargs,
        }
        out = QCSchemaToMolComponent.compute(inputs)
        if version:
            assert version == out.schema_version
        return out.schema_object
