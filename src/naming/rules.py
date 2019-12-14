# coding=utf-8
from __future__ import absolute_import, print_function

import re
import json
import os
from naming.serialize import Serializable
from naming.separators import get_separators
from naming.tokens import get_token
from naming.logger import logger

import six

_rules = {'_active': None}


class Rule(Serializable):
    def __init__(self, name):
        super(Rule, self).__init__()
        self.name = name
        self._fields = list()

    def add_fields(self, token_names):
        self._fields.extend(token_names)
        return True

    def solve(self, **values):
        """Build the name string with given values and return it"""
        result = None
        try:
            result = self.pattern.format(**values)
        except KeyError:
            symbols_dict = dict()
            for name, separator in six.iteritems(get_separators()):
                symbols_dict[name] = separator.symbol
            values.update(symbols_dict)
            result = self.pattern.format(**values)
        return result

    def parse(self, name):
        """Build and return dictionary with keys as tokens and values as given names"""
        delimiters = [value.symbol for key, value in six.iteritems(get_separators())]
        if len(delimiters) >= 1:
            regex_pattern = '(' + '|'.join(map(re.escape, delimiters)) + ')'
            name_parts = re.split(regex_pattern, name)
            retval = dict()
            for i, f in enumerate(self.fields):
                name_part = name_parts[i]
                token = get_token(f)
                if not token:
                    continue
                retval[f] = token.parse(name_part)
            return retval
        return None

    @property
    def pattern(self):
        return '{' + '}{'.join(self.fields) + '}'

    @property
    def fields(self):
        return tuple(self._fields)

    @fields.setter
    def fields(self, f):
        self._fields = f

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n


def add_rule(name, *fields):
    rule = Rule(name)
    rule.fields = fields
    _rules[name] = rule
    if get_active_rule() is None:
        set_active_rule(name)
    return rule


def remove_rule(name):
    if has_rule(name):
        del _rules[name]
        return True
    return False


def has_rule(name):
    return name in _rules.keys()


def reset_rules():
    _rules.clear()
    _rules['_active'] = None
    return True


def get_active_rule():
    name = _rules['_active']
    return _rules.get(name)


def set_active_rule(name):
    if has_rule(name):
        _rules['_active'] = name
        return True
    return False


def get_rule(name):
    return _rules.get(name)


def get_rules():
    return _rules


def save_rule(name, filepath):
    rule = get_rule(name)
    if not rule:
        return False
    with open(filepath, "w") as fp:
        json.dump(rule.data(), fp)
    return True


def load_rule(filepath):
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    rule = Rule.from_data(data)
    _rules[rule.name] = rule
    return True
