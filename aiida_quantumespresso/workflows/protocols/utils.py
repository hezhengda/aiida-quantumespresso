# -*- coding: utf-8 -*-
"""Utilities to manipulate the workflow input protocols."""
import functools
import os
import pathlib
import yaml


def recursive_merge(left, right):
    """Recursively merge two dictionaries into a single dictionary.

    :param left: first dictionary
    :param right: second dictionary
    :return: the recursively merged dictionary
    """
    import collections

    for key, value in left.items():
        if key in right:
            if isinstance(value, collections.abc.Mapping) and isinstance(right[key], collections.abc.Mapping):
                right[key] = recursive_merge(value, right[key])

    merged = left.copy()
    merged.update(right)

    return merged


def load_protocol_file(cls):
    """Load the protocol file for the given workflows class.

    :param cls: the workflow class.
    :return: the contents of the protocol file.
    """
    from aiida.plugins.entry_point import get_entry_point_from_class

    _, entry_point = get_entry_point_from_class(cls.__module__, cls.__name__)
    entry_point_name = entry_point.name
    parts = entry_point_name.split('.')
    parts.pop(0)
    filename = f'{parts.pop()}.yaml'
    basepath = functools.reduce(os.path.join, parts)

    with (pathlib.Path(__file__).resolve().parent / basepath / filename).open() as handle:
        return yaml.safe_load(handle)


def get_default_protocol(cls):
    """Return the default protocol for a given workflow class.

    :param cls: the workflow class.
    :return: the default protocol.
    """
    return load_protocol_file(cls)['default']


def get_available_protocols(cls):
    """Return the available protocols for a given workflow class.

    :param cls: the workflow class.
    :return: dictionary of available protocols, where each key is a protocol and value is another dictionary that
        contains at least the key `description` and optionally other keys with supplementary information.
    """
    data = load_protocol_file(cls)
    return {protocol: {'description': values['description']} for protocol, values in data['protocols'].items()}


def get_protocol_inputs(cls, protocol=None, overrides=None):
    """Return the inputs for the given workflow class and protocol.

    :param cls: the workflow class.
    :param protocol: optional specific protocol, if not specified, the default will be used
    :param overrides: dictionary of inputs that should override those specified by the protocol. The mapping should
        maintain the exact same nesting structure as the input port namespace of the corresponding workflow class.
    :return: mapping of inputs to be used for the workflow class.
    """
    data = load_protocol_file(cls)
    protocol = protocol or data['default']
    inputs = recursive_merge(data['base'], data['protocols'][protocol])
    inputs.pop('description')

    if overrides:
        return recursive_merge(inputs, overrides)

    return inputs


def get_magnetization_parameters() -> dict:
    """Return the mapping of suggested initial magnetic moments for each element.

    :returns: the magnetization parameters.
    """
    with (pathlib.Path(__file__).resolve().parent / 'magnetization.yaml').open() as handle:
        return yaml.safe_load(handle)


def get_initial_magnetization(structure, pseudo_family):
    """Return the dictionary with initial magnetization for each kind in the structure.

    :param structure: the structure.
    :param pseudo_family: pseudopotential family.
    :returns: dictionary of initial magnetizations.
    """
    magnetic_parameters = get_magnetization_parameters()
    initial_magnetization = {}

    for kind in structure.kinds:
        magnetic_moment = magnetic_parameters[kind.symbol]['magmom']

        if magnetic_moment == 0:
            magnetic_moment = magnetic_parameters['default']
        else:
            z_valence = pseudo_family.get_pseudo(element=kind.symbol).z_valence
            magnetic_moment /= float(z_valence)

        initial_magnetization[kind.name] = magnetic_moment

    return initial_magnetization
