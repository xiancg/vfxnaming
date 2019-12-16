# coding=utf-8
from __future__ import absolute_import, print_function

import copy
import json
import os
from naming.serialize import Serializable
from naming.logger import logger

import six

_tokens = dict()


class Token(Serializable):
    def __init__(self, name):
        """Tokens are the main parts of a naming rule. Each meaningful part of a name
        is called a token. A token can be required, meaning fully typed by the user,
        or can have a set of default options preconfigured.
        If options are present, then one of them is the default one.
        Each option follows a {full_name:abbreviation} schema, so that names can be short
        but meaning can be recovered easily.

        Args:
            name (str): Name that best describes the Token, this will be used as a way
            to invoke the Token object.
        """
        super(Token, self).__init__()
        self._name = name
        self._default = None
        self._options = dict()

    def add_option(self, key, value):
        """Add an option pair to this Token.

        Args:
            key (str): Full length name of the option
            value (str): Abbreviation to be used when building the name.
        """
        self._options[key] = value

    def solve(self, name=None):
        """Solve for abbreviation given a certain name. e.g.: center could return C

        Args:
            name (str, optional): Key to look for in the options for this Token.
                Defaults to None, which will return the default value set in the options
                for this Token.

        Raises:
            Exception: If Token is required and no value is passed.
            Exception: If given name is not found in options list.

        Returns:
            str: If Token is required, the same input value is returned
            str: If Token has options, the abbreviation for given name is returned
            str: If nothing is passed and Token has options, default option is returned.
        """
        if self.required and name:
            return name
        elif self.required and name is None:
            raise Exception("Token {} is required. name parameter must be passed.".format(self.name))
        elif not self.required and name:
            if name not in self._options.keys():
                raise Exception(
                    "name '{}' not found in Token '{}'. Options: {}".format(
                        name, self.name, ', '.join(self._options.keys())
                        )
                    )
            return self._options.get(name)
        elif not self.required and not name:
            return self.default

    def parse(self, value):
        """Get metatada (origin) for given value in name. e.g.: L could return left

        Args:
            value (str): Name part to be parsed to the token origin

        Returns:
            str: Token origin for given value or value itself if no match is found.
        """
        if len(self._options) >= 1:
            for k, v in six.iteritems(self._options):
                if v == value:
                    return k
        return value

    @property
    def required(self):
        return self.default is None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def default(self):
        if self._default is None and len(self._options) >= 1:
            self._default = self._options.values()[0]
        return self._default

    @default.setter
    def default(self, d):
        if len(self._options) >= 1:
            if d in self._options.values():
                self._default = d

    @property
    def options(self):
        return copy.deepcopy(self._options)


class TokenNumber(Serializable):
    def __init__(self, name):
        super(TokenNumber, self).__init__()
        self._name = name
        self._default = 1
        self._options = {"prefix": "", "suffix": "", "padding": 3}

    def solve(self, number):
        """Solve for number with given padding parameter.
            e.g.: 1 with padding 3, will return 001
        """
        numberStr = str(number).zfill(self.padding)
        return '{}{}{}'.format(self.prefix, numberStr, self.suffix)

    def parse(self, value):
        """Get metatada (number) for given value in name. e.g.: v0025 will return 25"""
        if value.isdigit():
            return int(value)
        else:
            prefix_index = 0
            for each in value[::1]:
                if each.isdigit() and prefix_index == 0:
                    prefix_index = -1
                    break
                elif each.isdigit() and prefix_index > 0:
                    break
                prefix_index += 1

            suffix_index = 0
            for each in value[::-1]:
                if each.isdigit() and suffix_index == 0:
                    suffix_index = -1
                    break
                elif each.isdigit() and suffix_index > 0:
                    break
                suffix_index += 1

            if prefix_index == -1 and suffix_index >= 0:
                return int(value[:-suffix_index])
            elif prefix_index >= 0 and suffix_index == -1:
                return int(value[prefix_index:])
            elif prefix_index >= 0 and suffix_index >= 0:
                return int(value[prefix_index:-suffix_index])

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def default(self):
        return self._default

    @property
    def required(self):
        return True

    @property
    def padding(self):
        return self._options.get('padding')

    @padding.setter
    def padding(self, p):
        if p <= 0:
            p = 1
        self._options['padding'] = int(p)

    @property
    def prefix(self):
        return self._options.get('prefix')

    @prefix.setter
    def prefix(self, p):
        # ! Check for non digit and string type
        self._options['prefix'] = p

    @property
    def suffix(self):
        return self._options.get('suffix')

    @suffix.setter
    def suffix(self, s):
        # ! Check for string type
        self._options['suffix'] = s

    @property
    def options(self):
        return copy.deepcopy(self._options)


def add_token(name, **kwargs):
    token = Token(name)
    for k, v in six.iteritems(kwargs):
        if k == "default":
            token.default = v
            continue
        token.add_option(k, v)
    _tokens[name] = token
    return token


def add_token_number(name, prefix=str(), suffix=str(), padding=3):
    token = TokenNumber(name)
    token.prefix = prefix
    token.suffix = suffix
    token.padding = padding
    _tokens[name] = token
    return token


def remove_token(name):
    if has_token(name):
        del _tokens[name]
        return True
    return False


def has_token(name):
    return name in _tokens.keys()


def reset_tokens():
    _tokens.clear()
    return True


def get_token(name):
    return _tokens.get(name)


def get_tokens():
    return _tokens


def save_token(name, filepath):
    token = get_token(name)
    if not token:
        return False
    with open(filepath, "w") as fp:
        json.dump(token.data(), fp)
    return True


def load_token(filepath):
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    class_name = data.get("_Serializable_classname")
    logger.debug("Loading token type: {}".format(class_name))
    token = eval("{}.from_data(data)".format(class_name))
    _tokens[token.name] = token
    return True
