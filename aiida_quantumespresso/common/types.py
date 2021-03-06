# -*- coding: utf-8 -*-
"""Module with common data types."""
import enum


class RelaxType(enum.Enum):
    """Enumeration of known relax types."""

    NONE = 'none'  # All degrees of freedom are fixed, essentially performs single point SCF calculation
    ATOMS = 'atoms'  # Only the atomic positions are relaxed, cell is fixed
    VOLUME = 'volume'  # Only the cell volume is optimized, cell shape and atoms are fixed
    SHAPE = 'shape'  # Only the cell shape is optimized at a fixed volume and fixed atomic positions
    CELL = 'cell'  # Only the cell is optimized, both shape and volume, while atomic positions are fixed
    ATOMS_VOLUME = 'atoms_volume'  # Same as `VOLUME` but atomic positions are relaxed as well
    ATOMS_SHAPE = 'atoms_shape'  # Same as `SHAPE`  but atomic positions are relaxed as well
    ATOMS_CELL = 'atoms_cell'  # Same as `CELL`  but atomic positions are relaxed as well
