# coding=utf-8
from __future__ import absolute_import, print_function

import json
import os
import copy
import platform
from cgx_naming.serialize import Serializable

_separators = dict()


class Separator(Serializable):
    def __init__(self, name):
        """Separators are what splits one token from another. This objects
        allows using multiple system allowed characters as separators. Usually
        separators are '_', '-' or '.', so these are the allowed defaults for
        the object, but you can append to the list. Default symbol is '_'

        Args:
            name (str): Name that best describes the separator.
        """
        super(Separator, self).__init__()
        self._name = name
        self._allowed_symbols = ['_', '-', '.']
        self._symbol = '_'

    def add_allowed_symbol(self, symbol):
        """Add given character symbol to allowed symbols list.

        Args:
            symbol (str): A character separator. e.g.: '_', '-', '.'

        Returns:
            bool: True if symbol was added, False otherwise.
        """
        if symbol not in self._allowed_symbols:
            self._allowed_symbols.append(symbol)
            return True
        return False

    def remove_allowed_symbol(self, symbol):
        """Remove given character symbol from allowed symbols list.

        Args:
            symbol (str): An existing character separator. e.g.: '_', '-', '.'

        Returns:
            bool: True if symbol was removed, False otherwise.
        """
        if symbol in self._allowed_symbols:
            self._allowed_symbols.remove(symbol)
            return True
        return False

    def use_folder_separators(self):
        """"Convenience function to swap file or object naming separators,
        by folder structure separators: '\\' and '/'.

        Symbol will be set to '\\' by default
        """
        self._allowed_symbols = ["\\", "/"]
        this_os = platform.system()
        if this_os == "Windows":
            self._symbol = "\\"
        elif this_os == "Linux":
            self._symbol = "/"
        elif this_os == "Darwin":
            self._symbol = "/"
        else:
            self._symbol = "/"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, s):
        if s in self._allowed_symbols:
            self._symbol = s

    @property
    def allowed_symbols(self):
        return copy.deepcopy(self._allowed_symbols)


def add_separator(name, symbol='_'):
    """Add separator to current naming session.

    Args:
        name (str): Name that best describes the separator
        symbol (str, optional): Symbol to be used as separator.
        Tip: Use a single character. Defaults to '_'.

    Returns:
        Separator: The Separator object instance created.
    """
    separator = Separator(name)
    separator.symbol = symbol
    _separators[name] = separator
    return separator


def remove_separator(name):
    """Remove Separator from current session.

    Args:
        name (str): The name of the separator to be removed.

    Returns:
        bool: True if successful, False if a separator name was not found.
    """
    if has_separator(name):
        del _separators[name]
        return True
    return False


def has_separator(name):
    """Test if current session has a separator with given name.

    Args:
        name (str): The name of the separator to be looked for.

    Returns:
        bool: True if separator with given name exists in current session, False otherwise.
    """
    return name in _separators.keys()


def reset_separators():
    """Clears all separators created for current session.

    Returns:
        bool: True if clearing was successful.
    """
    _separators.clear()
    return True


def get_separator(name):
    """Gets Separator object with given name.

    Args:
        name (str): The name of the separator to query.

    Returns:
        Separator: Separator object instance for given name.
    """
    return _separators.get(name)


def get_separators():
    """Get all Separator objects for current session.

    Returns:
        dict: {separator_name:Separator}
    """
    return _separators


def save_separator(name, filepath):
    """Saves given separator serialized to specified location.

    Args:
        name (str): The name of the separator to be saved.
        filepath (str): Path location to save the separator.

    Returns:
        bool: True if successful, False if separator wasn't found in current session.
    """
    token = get_separator(name)
    if not token:
        return False
    with open(filepath, "w") as fp:
        json.dump(token.data(), fp)
    return True


def load_separator(filepath):
    """Load separator from given location and create Separator object in memory to
    work with it.

    Args:
        filepath (str): Path to existing .separator file location

    Returns:
        bool: True if successful, False if .separator wasn't found.
    """
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    separator = Separator.from_data(data)
    _separators[separator.name] = separator
    return True
