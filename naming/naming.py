# coding=utf-8
'''
Heavily based upon the work of Cesar Saez https://www.cesarsaez.me
'''
from __future__ import absolute_import, print_function

import copy
import os
import json

import six

# TODO: Add separator functionality

NAMING_REPO_ENV = "NAMING_REPO"
_rules = {'_active': None}
_tokens = dict()


class Serializable(object):
    def data(self):
        retval = copy.deepcopy(self.__dict__)
        retval["_Serializable_classname"] = type(self).__name__
        retval["_Serializable_version"] = "1.0"
        return retval

    @classmethod
    def fromData(cls, data):
        if data.get("_Serializable_classname") != cls.__name__:
            return None
        del data["_Serializable_classname"]
        if data.get("_Serializable_version") is not None:
            del data["_Serializable_version"]

        if cls.__name__ == 'Rule':
            this = cls(None, [None])
        else:
            this = cls(None)
        this.__dict__.update(data)
        return this


class Token(Serializable):
    def __init__(self, name):
        super(Token, self).__init__()
        self._name = name
        self._default = None
        self._options = dict()

    def addOption(self, key, value):
        self._options[key] = value

    def solve(self, name=None):
        """Solve for abbreviation given a certain name. Ex: center could return C"""
        if name is None:
            return self.default
        return self._options.get(name)

    def parse(self, value):
        """Get metatada (origin) for given value in name. Ex: L could return left"""
        for k, v in six.iteritems(self._options):
            if v == value:
                return k

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
        self._default = d

    @property
    def options(self):
        return copy.deepcopy(self._options)

    @property
    def isNumber(self):
        return False


class TokenNumber(Token):
    def __init__(self, name):
        super(TokenNumber, self).__init__(name)
        self._isNumber = True

    def solve(self, number):
        """Solve for number with given padding parameter.
            Ex: 1 could return 001 with padding 3"""
        numberStr = str(number).zfill(self.padding)
        return '{}{}{}'.format(self.prefix, numberStr, self.suffix)

    def parse(self, value):
        """Get metatada (number) for given value in name. Ex: v0025 could return 25"""
        if value.isdigit():
            return int(value)
        else:
            prefixIndex = 0
            for each in value[::1]:
                if each.isdigit() and prefixIndex == 0:
                    prefixIndex = -1
                    break
                if not each.isdigit():
                    prefixIndex += 1
                else:
                    break
            suffixIndex = 0
            for each in value[::-1]:
                if each.isdigit() and suffixIndex == 0:
                    suffixIndex = -1
                    break
                if not each.isdigit():
                    suffixIndex += 1
                else:
                    break

            if prefixIndex == -1 and suffixIndex >= 0:
                return int(value[:-suffixIndex])
            elif prefixIndex >= 0 and suffixIndex == -1:
                return int(value[prefixIndex:])
            elif prefixIndex >= 0 and suffixIndex >= 0:
                return int(value[prefixIndex:-suffixIndex])

    @property
    def padding(self):
        return self._options['padding']

    @padding.setter
    def padding(self, p):
        if p <= 0:
            p = 1
        self._options['padding'] = int(p)

    @property
    def prefix(self):
        return self._options['prefix']

    @prefix.setter
    def prefix(self, p):
        self._options['prefix'] = p

    @property
    def suffix(self):
        return self._options['suffix']

    @suffix.setter
    def suffix(self, s):
        self._options['suffix'] = s

    @property
    def default(self):
        self._default = 1
        return self._default

    @property
    def required(self):
        return True

    @property
    def isNumber(self):
        return True


class Rule(Serializable):
    def __init__(self, name, fields):
        super(Rule, self).__init__()
        self.name = name
        self._fields = list()
        self.addFields(fields)

    def addFields(self, tokenNames):
        self._fields.extend(tokenNames)
        return True

    def solve(self, **values):
        """Build the name string with given values and return it"""
        return self._pattern.format(**values)

    def parse(self, name):
        """Build and return dictionary with keys as tokens and values as given names"""
        retval = dict()
        splitName = name.split('_')
        for i, f in enumerate(self.fields):
            namePart = splitName[i]
            token = _tokens[f]
            if token.required:
                if token.isNumber:
                    retval[f] = token.parse(namePart)
                else:
                    retval[f] = namePart
                continue
            retval[f] = token.parse(namePart)
        return retval

    @property
    def _pattern(self):
        return '{' + '}_{'.join(self.fields) + '}'

    @property
    def fields(self):
        return tuple(self._fields)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n


def addRule(name, *fields):
    rule = Rule(name, fields)
    _rules[name] = rule
    if getActiveRule() is None:
        setActiveRule(name)
    return rule


def removeRule(name):
    if hasRule(name):
        del _rules[name]
        return True
    return False


def hasRule(name):
    return name in _rules.keys()


def resetRules():
    _rules.clear()
    _rules['_active'] = None
    return True


def getActiveRule():
    name = _rules['_active']
    return _rules.get(name)


def setActiveRule(name):
    if hasRule(name):
        _rules['_active'] = name
        return True
    return False


def getRule(name):
    return _rules.get(name)


def saveRule(name, filepath):
    rule = getRule(name)
    if not rule:
        return False
    with open(filepath, "w") as fp:
        json.dump(rule.data(), fp)
    return True


def loadRule(filepath):
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    rule = Rule.fromData(data)
    _rules[rule.name] = rule
    return True


def addToken(name, **kwargs):
    token = Token(name)
    for k, v in six.iteritems(kwargs):
        if k == "default":
            token.default = v
            continue
        token.addOption(k, v)
    _tokens[name] = token
    return token


def removeToken(name):
    if hasToken(name):
        del _tokens[name]
        return True
    return False


def hasToken(name):
    return name in _tokens.keys()


def resetTokens():
    _tokens.clear()
    return True


def getToken(name):
    return _tokens.get(name)


def saveToken(name, filepath):
    token = getToken(name)
    if not token:
        return False
    with open(filepath, "w") as fp:
        json.dump(token.data(), fp)
    return True


def loadToken(filepath):
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    if data.get("_Serializable_classname") == 'TokenNumber':
        token = TokenNumber.fromData(data)
    else:
        token = Token.fromData(data)
    _tokens[token.name] = token
    return True


def addTokenNumber(name, prefix='', padding=3, suffix=''):
    token = TokenNumber(name)
    token.addOption('prefix', prefix)
    token.addOption('padding', padding)
    token.addOption('suffix', suffix)
    _tokens[name] = token
    return token


def parse(name):
    rule = getActiveRule()
    return rule.parse(name)


def solve(*args, **kwargs):
    values = dict()
    rule = getActiveRule()
    i = 0
    for f in rule.fields:
        token = _tokens[f]
        if isinstance(token, TokenNumber):
            if kwargs.get(f) is not None:
                values[f] = token.solve(kwargs[f])
                continue
            values[f] = token.solve(args[i])
            i += 1
            continue
        if token.required:
            if kwargs.get(f) is not None:
                values[f] = kwargs[f]
                continue
            values[f] = args[i]
            i += 1
            continue
        values[f] = token.solve(kwargs.get(f))

    return rule.solve(**values)


def getRepo():
    env_repo = os.environ.get(NAMING_REPO_ENV)
    local_repo = os.path.join(os.path.expanduser("~"), ".NXATools", "naming")
    return env_repo or local_repo


def saveSession(repo=None):
    repo = repo or getRepo()
    if not os.path.exists(repo):
        os.mkdir(repo)
    # tokens and rules
    for name, token in six.iteritems(_tokens):
        filepath = os.path.join(repo, name + ".token")
        saveToken(name, filepath)
    for name, rule in six.iteritems(_rules):
        if not isinstance(rule, Rule):
            continue
        filepath = os.path.join(repo, name + ".rule")
        saveRule(name, filepath)
    # extra configuration
    active = getActiveRule()
    config = {"setActiveRule": active.name if active else None}
    filepath = os.path.join(repo, "naming.conf")
    with open(filepath, "w") as fp:
        json.dump(config, fp, indent=4)
    return True


def loadSession(repo=None):
    repo = repo or getRepo()
    # tokens and rules
    for dirpath, dirnames, filenames in os.walk(repo):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filename.endswith(".token"):
                loadToken(filepath)
            elif filename.endswith(".rule"):
                loadRule(filepath)
    # extra configuration
    filepath = os.path.join(repo, "naming.conf")
    if os.path.exists(filepath):
        with open(filepath) as fp:
            config = json.load(fp)
        for k, v in six.iteritems(config):
            globals()[k](v)  # executes setActiveRule and sets it
    return True
