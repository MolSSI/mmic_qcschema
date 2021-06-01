from typing import Dict, Any, List, Tuple, Optional
import qcelemental
import mmelemental

from mmic_translator import (
    TransComponent,
    TransInput,
    TransOutput,
)

__all__ = ["MolToQCSchemaComponent", "QCSchemaToMolComponent"]


class MolToQCSchemaComponent(TransComponent):
    """A component for converting MMSchema to QCSchema molecule."""

    def execute(
        self,
        inputs: TransInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, TransOutput]:
        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        mmol = inputs.schema_object
        if mmol.atomic_numbers is None:
            raise NotImplementedError(
                "QCSchema supports only atomic molecules. Molecule.atomic_numbers must be defined."
            )

        if mmol.ndim != 3:
            raise NotImplementedError("QCSchema supports only 3D molecules")

        assert (
            inputs.schema_object.schema_version == 1
        ), "This converter works only with mmschema_molecule version 1"

        geo_factor = qcelemental.constants.conversion_factor(
            mmol.geometry_units, "bohr"
        )
        coordinates = mmol.geometry * geo_factor

        charge_factor = qcelemental.constants.conversion_factor(
            mmol.molecular_charge_units, "elementary_charge"
        )
        mol_charge = charge_factor * mmol.molecular_charge

        mass_factor = qcelemental.constants.conversion_factor(
            mmol.masses_units, "atomic_mass_unit"
        )
        masses = mass_factor * mmol.masses  # ignore masses for now

        extras = mmol.extras

        # atom_labels in qcel are treated in lower case ... so
        # we store atom_labels from MMSchema in extras instead
        if extras is not None:
            if mmol.atom_labels is not None:
                extras.update({"atom_labels": mmol.atom_labels})
        elif mmol.atom_labels is not None:
            extras = {"atom_labels": mmol.atom_labels, "masses_mmel": masses}

        data = {
            "atomic_numbers": mmol.atomic_numbers,
            "mass_numbers": mmol.mass_numbers,
            "symbols": mmol.symbols,
            "geometry": coordinates,
            "connectivity": mmol.connectivity,
            "molecular_charge": mol_charge,
            "comment": mmol.comment,
            "identifiers": mmol.identifiers,
            "extras": extras,
        }

        qmol = qcelemental.models.Molecule(**data, validate=True, nonphysical=False)

        return True, TransOutput(proc_input=inputs, data_object=qmol)


class QCSchemaToMolComponent(TransComponent):
    """A component for converting ParmEd molecule to Molecule object."""

    def execute(
        self,
        inputs: TransInput,
        extra_outfiles: Optional[List[str]] = None,
        extra_commands: Optional[List[str]] = None,
        scratch_name: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Tuple[bool, TransOutput]:

        if isinstance(inputs, dict):
            inputs = self.input()(**inputs)

        assert (
            inputs.data_object.schema_version == 2
        ), "This converter works only with qcschema_molecule version 2"

        qcmol = inputs.data_object

        mm_units = mmelemental.models.Molecule.get_units()
        geo_factor = qcelemental.constants.conversion_factor(
            "bohr", mm_units["geometry_units"]
        )
        coordinates = qcmol.geometry.flatten() * geo_factor

        charge_factor = qcelemental.constants.conversion_factor(
            "elementary_charge", mm_units["molecular_charge_units"]
        )
        mol_charge = charge_factor * qcmol.molecular_charge

        mass_factor = qcelemental.constants.conversion_factor(
            "atomic_mass_unit", mm_units["masses_units"]
        )
        masses = mass_factor * qcmol.masses

        # since qcel treats atom_labels in lower case, we get
        # them instead from extras
        if qcmol.extras is not None:
            atom_labels = qcmol.extras.pop("atom_labels", None)
        else:
            atom_labels = None

        input_dict = {
            "atomic_numbers": qcmol.atomic_numbers,
            "mass_numbers": qcmol.mass_numbers
            if all(qcmol.mass_numbers > 0)
            else None,  # qcel can return mass_number = -1, which likely means
            # the masses are inconsistent with the mass_numbers
            "symbols": qcmol.symbols,
            "geometry": coordinates,
            "connectivity": qcmol.connectivity,
            "masses": masses,
            "molecular_charge": mol_charge,
            "atom_labels": atom_labels,
            "comment": qcmol.comment,
            "identifiers": qcmol.identifiers,
            "extras": qcmol.extras,
        }

        return True, TransOutput(
            proc_input=inputs, schema_object=mmelemental.models.Molecule(**input_dict)
        )
