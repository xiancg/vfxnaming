# coding=utf-8
from __future__ import absolute_import, print_function

import re
import json
import os
from vfxnaming.serialize import Serializable
from vfxnaming.separators import get_separators
from vfxnaming.tokens import get_token
from vfxnaming.logger import logger
from vfxnaming.error import ParsingError, SolvingError

import six

_rules = {'_active': None}


class Rule(Serializable):
    """Each rule is managed by an instance of this class. Fields exist for each
    Token and Separator used in the rule definition.

    Args:
        ``name`` (str): Name that best describes the rule, this will be used as a way
        to query the Rule object.

        ``pattern`` (str): The template pattern to use, which uses existing Tokens.
        e.g.: '{side}_{region}_{side}_{region}.png'

        ``anchor``: ([Rule.ANCHOR_START, Rule.ANCHOR_END, Rule.ANCHOR_BOTH], optional):
        For parsing, regex matching will look for a match from this Anchor. If a
        pattern is anchored to the start, it requires the start of a passed path to
        match the pattern. Defaults to ANCHOR_START.
    """

    __FIELDS_REGEX = re.compile(r'{(.+?)}')
    ANCHOR_START, ANCHOR_END, ANCHOR_BOTH = (1, 2, 3)

    def __init__(self, name, pattern, anchor=ANCHOR_START):
        super(Rule, self).__init__()
        self._name = name
        self._raw_pattern = pattern
        self._pattern = self.__init_pattern()
        self._anchor = anchor
        self._regex = self.__build_regex()

    def solve(self, **values):
        """Given arguments are used to build a name.

        Raises:
            SolvingError: Arguments passed do not match with rule fields.

        Returns:
            str: A string with the resulting name.
        """
        result = None
        separators = get_separators()
        if separators:
            has_separators = set(separators.keys()).intersection(self.fields)
            if len(has_separators) > 0:
                symbols_dict = dict()
                for name, separator in six.iteritems(get_separators()):
                    symbols_dict[name] = separator.symbol
                values.update(symbols_dict)
        try:
            result = self.pattern.format(**values)
        except KeyError as why:
            field_names = ", ".join(self.fields)
            raise SolvingError(
                "Arguments passed do not match with naming rule fields {}\n{}".format(
                    field_names, why
                )
            )

        return result

    def parse(self, name):
        """Build and return dictionary with keys as tokens and values as given names.

        If your rule uses the same token more than once, the returned dictionary keys
        will have the token name and an incremental digit next to them so they can be
        differentiated.

        Args:
            name (str): Name string e.g.: C_helmet_001_MSH

        Returns:
            dict: A dictionary with keys as tokens and values as given name parts.
            e.g.: {'side':'C', 'part':'helmet', 'number': 1, 'type':'MSH'}
        """
        delimiters = [value.symbol for key, value in six.iteritems(get_separators())]
        if len(delimiters) >= 1:
            logger.debug("Parsing with these separators: {}".format(', '.join(delimiters)))
            regex_pattern = '(' + '|'.join(map(re.escape, delimiters)) + ')'
            name_parts = re.split(regex_pattern, name)
            if len(name_parts) != len(self.fields):
                raise ParsingError("Missing tokens from passed name. Found {}".format(", ".join(name_parts)))
            logger.debug("Name parts: {}".format(", ".join(name_parts)))

            repeated_fields = dict()
            for each in self.fields:
                if each not in get_separators().keys() and each not in repeated_fields.keys():
                    if self.fields.count(each) > 1:
                        repeated_fields[each] = 1
            if repeated_fields:
                logger.debug(
                    "Repeated tokens: {}".format(", ".join(repeated_fields.keys()))
                )

            retval = dict()
            for i, f in enumerate(self.fields):
                name_part = name_parts[i]
                token = get_token(f)
                if not token:
                    continue
                if f in repeated_fields.keys():
                    counter = repeated_fields.get(f)
                    repeated_fields[f] = counter + 1
                    f = "{}{}".format(f, counter)
                retval[f] = token.parse(name_part)
            return retval
        logger.warning(
            "No separators used for rule {}, parsing is not possible.".format(
                self.name
            )
        )
        return None

    def __init_pattern(self):
        # * This accounts for those cases where a token is used more than once in a rule
        pattern_digits = self._raw_pattern
        for each in list(set(self.fields)):
            regex_pattern = re.compile(each)
            indexes = [match.end() for match in regex_pattern.finditer(pattern_digits)]
            repetetions = len(indexes)
            if repetetions > 1:
                i = 0
                for match in sorted(indexes, reverse=True):
                    pattern_digits = "{}{}{}".format(
                        pattern_digits[:match],
                        str(repetetions-i),
                        pattern_digits[match:]
                    )
                    i += 1
        return pattern_digits

    @property
    def pattern(self):
        return self._raw_pattern

    @property
    def fields(self):
        """
        Returns:
            [tuple]: Tuple of all Tokens found in this Rule's pattern
        """
        return tuple(self.__FIELDS_REGEX.findall(self._raw_pattern))

    @property
    def regex(self):
        """
        Returns:
            [str]: Regular expression used to parse from this Rule
        """
        return self._regex

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n


def add_rule(name, pattern, anchor=Rule.ANCHOR_START):
    """Add rule to current naming session. If no active rule is found, it adds
    the created one as active by default.

    Args:
        ``name`` (str): Name that best describes the rule, this will be used as a way
        to invoke the Rule object.

        ``pattern`` (str): The template pattern to use, which uses existing Tokens.
        e.g.: '{side}_{region}_{side}_{region}.png'

        ``anchor``: ([Rule.ANCHOR_START, Rule.ANCHOR_END, Rule.ANCHOR_BOTH], optional):
        For parsing, regex matching will look for a match from this Anchor. If a
        pattern is anchored to the start, it requires the start of a passed path to
        match the pattern. Defaults to ANCHOR_START.

    Returns:
        Rule: The Rule object instance created for given name and fields.
    """
    rule = Rule(name, pattern, anchor)
    _rules[name] = rule
    if get_active_rule() is None:
        set_active_rule(name)
        logger.debug("No active rule found, setting this one as active: {}".format(name))
    return rule


def remove_rule(name):
    """Remove Rule from current session.

    Args:
        name (str): The name of the rule to be removed.

    Returns:
        bool: True if successful, False if a rule name was not found.
    """
    if has_rule(name):
        del _rules[name]
        return True
    return False


def has_rule(name):
    """Test if current session has a rule with given name.

    Args:
        name (str): The name of the rule to be looked for.

    Returns:
        bool: True if rule with given name exists in current session, False otherwise.
    """
    return name in _rules.keys()


def reset_rules():
    """Clears all rules created for current session.

    Returns:
        bool: True if clearing was successful.
    """
    _rules.clear()
    _rules['_active'] = None
    return True


def get_active_rule():
    """Get currently active rule for the session. This is the rule
    that will be used to parse and solve from.

    Returns:
        Rule: Rule object instance for currently active Rule.
    """
    name = _rules.get('_active')
    return _rules.get(name)


def set_active_rule(name):
    """Sets given rule as active for the session. This it the rule that's
    being used to parse and solve from.

    Args:
        name (str): The name of the rule to be activated.

    Returns:
        bool: True if successful, False otherwise.
    """
    if has_rule(name):
        _rules['_active'] = name
        return True
    return False


def get_rule(name):
    """Gets Rule object with given name.

    Args:
        name (str): The name of the rule to query.

    Returns:
        Rule: Rule object instance for given name.
    """
    return _rules.get(name)


def get_rules():
    """Get all Rule objects for current session.

    Returns:
        dict: {rule_name:Rule}
    """
    return _rules


def save_rule(name, directory):
    """Saves given rule serialized to specified location.

    Args:
        ``name`` (str): The name of the rule to be saved.

        ``directory`` (str): Path location to save the rule.

    Returns:
        bool: True if successful, False if rule wasn't found in current session.
    """
    rule = get_rule(name)
    if not rule:
        return False
    file_name = "{}.rule".format(name)
    filepath = os.path.join(directory, file_name)
    with open(filepath, "w") as fp:
        json.dump(rule.data(), fp)
    return True


def load_rule(filepath):
    """Load rule from given location and create Rule object in memory to work with it.

    Args:
        filepath (str): Path to existing .rule file location

    Returns:
        bool: True if successful, False if .rule wasn't found.
    """
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    new_rule = Rule.from_data(data)
    if new_rule:
        _rules[new_rule.name] = new_rule
        return True
    return False
