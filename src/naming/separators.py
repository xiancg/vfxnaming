# coding=utf-8
from __future__ import absolute_import, print_function

import json
import os
from naming.serialize import Serializable
from naming.logger import logger

_separators = dict()


class Separator(Serializable):
    def __init__(self, name):
        super(Separator, self).__init__()
        self._name = name
        self._allowed_symbols = ['_', '-', '.']
        self._symbol = '_'

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
        return self._allowed_symbols

    def add_allowed_symbol(self, s):
        if s not in self._allowed_symbols:
            self._allowed_symbols.append(s)

    def remove_allowed_symbol(self, s):
        if s in self._allowed_symbols:
            self._allowed_symbols.remove(s)


def add_separator(name, symbol='_'):
    separator = Separator(name)
    separator.symbol = symbol
    _separators[name] = separator
    return separator


def remove_separator(name):
    if has_separator(name):
        del _separators[name]
        return True
    return False


def has_separator(name):
    return name in _separators.keys()


def reset_separators():
    _separators.clear()
    return True


def get_separator(name):
    return _separators.get(name)


def get_separators():
    return _separators


def save_separator(name, filepath):
    token = get_separator(name)
    if not token:
        return False
    with open(filepath, "w") as fp:
        json.dump(token.data(), fp)
    return True


def load_separator(filepath):
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    class_name = data.get("_Serializable_classname")
    separator = eval("{}.from_data(data)".format(class_name))
    _separators[separator.name] = separator
    return True
