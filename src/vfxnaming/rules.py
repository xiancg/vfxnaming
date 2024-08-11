import re
import json
import sys
import functools
from pathlib import Path
from collections import defaultdict
from typing import Dict, AnyStr, Union, Tuple

from vfxnaming.serialize import Serializable
from vfxnaming.tokens import get_token
from vfxnaming.logger import logger
from vfxnaming.error import ParsingError, SolvingError, RuleError

_rules = {"_active": None}


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

    __FIELDS_REGEX = re.compile(r"{(.+?)}")
    __PATTERN_SEPARATORS_REGEX = re.compile(
        r"(}[_\-\.:\|/\\]{|[_\-\.:\|/\\]{|}[_\-\.:\|/\\])"
    )
    __SEPARATORS_REGEX = re.compile(r"[_\-\.:\|/\\]")
    ANCHOR_START, ANCHOR_END, ANCHOR_BOTH = (1, 2, 3)

    def __init__(self, name, pattern, anchor=ANCHOR_START):
        super(Rule, self).__init__()
        self._name: str = name
        self._pattern: str = pattern
        self._anchor: int = anchor
        self._regex: re.Pattern = self.__build_regex()

    def data(self) -> Dict:
        """Collect all data for this object instance.

        Returns:
            dict: {attribute:value}
        """
        retval = dict()
        retval["_name"] = self._name
        retval["_pattern"] = self._pattern
        retval["_anchor"] = self._anchor
        retval["_Serializable_classname"] = type(self).__name__
        retval["_Serializable_version"] = "1.0"
        return retval

    @classmethod
    def from_data(cls, data) -> "Rule":
        """Create object instance from give data. Used by Rule,
        Token, Separator to create object instances from disk saved data.

        Args:
            data (dict): {attribute:value}

        Returns:
            Serializable: Object instance for Rule, Token or Separator.
        """
        # Validation
        if data.get("_Serializable_classname") != cls.__name__:
            return None
        del data["_Serializable_classname"]
        if data.get("_Serializable_version") is not None:
            del data["_Serializable_version"]

        this = cls(data.get("_name"), data.get("_pattern"), data.get("_anchor"))
        return this

    def solve(self, **values) -> AnyStr:
        """Given arguments are used to build a name.

        Raises:
            SolvingError: Arguments passed do not match with rule fields.

        Returns:
            str: A string with the resulting name.
        """
        result = None

        try:
            result = self.__digits_pattern().format(**values)
        except KeyError as why:
            raise SolvingError(
                f"Arguments passed do not match with naming rule fields {self._pattern}\n{why}"
            )

        return result

    def parse(self, name: AnyStr) -> Union[Dict, None]:
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
        expected_separators = self.__PATTERN_SEPARATORS_REGEX.findall(self._pattern)
        if len(expected_separators) <= 0:
            logger.warning(
                f"No separators used for rule '{self.name}', parsing is not possible."
            )
            return None
        name_separators = self.__SEPARATORS_REGEX.findall(name)
        if len(expected_separators) <= len(name_separators):
            retval = dict()
            match = self._regex.search(name)
            if match:
                name_parts = sorted(match.groupdict().items())
                name_parts_str = ", ".join(
                    [f"('{k[:-3]}': '{v}')" for k, v in name_parts]
                )
                logger.debug(f"Name parts: {name_parts_str}")
                repeated_fields = dict()
                for each in self.fields:
                    if each not in repeated_fields.keys():
                        if self.fields.count(each) > 1:
                            repeated_fields[each] = 1
                if repeated_fields:
                    logger.debug(f"Repeated tokens: {', '.join(repeated_fields.keys())}")

                for key, value in name_parts:
                    # Strip number that was added to make group name unique
                    token_name = key[:-3]
                    token = get_token(token_name)
                    if not token:
                        continue
                    if token_name in repeated_fields.keys():
                        counter = repeated_fields.get(token_name)
                        repeated_fields[token_name] = counter + 1
                        token_name = f"{token_name}{counter}"
                    retval[token_name] = token.parse(value)
            return retval
        else:
            raise ParsingError(
                f"Separators count mismatch between given name '{name}':'{len(name_separators)}' "
                f"and rule's pattern '{self._pattern}':'{len(expected_separators)}'."
            )

    def __build_regex(self) -> re.Pattern:
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        # Escape non-placeholder components
        expression = re.sub(
            r"(?P<placeholder>{(.+?)(:(\\}|.)+?)?})|(?P<other>.+?)",
            self.__escape,
            self._pattern,
        )
        # Replace placeholders with regex pattern
        expression = re.sub(
            r"{(?P<placeholder>.+?)(:(?P<expression>(\\}|.)+?))?}",
            functools.partial(self.__convert, placeholder_count=defaultdict(int)),
            expression,
        )

        if self._anchor is not None:
            if bool(self._anchor & self.ANCHOR_START):
                expression = f"^{expression}"

            if bool(self._anchor & self.ANCHOR_END):
                expression = f"{expression}$"
        # Compile expression
        try:
            compiled = re.compile(expression)
        except re.error as error:
            if any(
                [
                    "bad group name" in str(error),
                    "bad character in group name" in str(error),
                ]
            ):
                raise ValueError("Placeholder name contains invalid characters.")
            else:
                _, value, traceback = sys.exc_info()
                message = f"Invalid pattern: {value}"
                raise ValueError(message).with_traceback(traceback)

        return compiled

    def __convert(self, match: re.Match, placeholder_count: int) -> AnyStr:
        """Return a regular expression to represent *match*.

        ``placeholder_count`` should be a ``defaultdict(int)`` that will be used to
        store counts of unique placeholder names.

        """
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        placeholder_name = match.group("placeholder")

        # The re module does not support duplicate group names. To support
        # duplicate placeholder names in templates add a unique count to the
        # regular expression group name and strip it later during parse.
        placeholder_count[placeholder_name] += 1
        placeholder_name += "{0:03d}".format(placeholder_count[placeholder_name])

        expression = match.group("expression")
        if expression is None:
            expression = r"[\w_.\-/:]+"

        # Un-escape potentially escaped characters in expression.
        expression = expression.replace("{", "{").replace("}", "}")

        return r"(?P<{0}>{1})".format(placeholder_name, expression)

    def __escape(self, match: re.Match) -> AnyStr:
        """Escape matched 'other' group value."""
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        groups = match.groupdict()
        if groups.get("other"):
            return re.escape(groups.get("other"))
        return groups.get("placeholder")

    def __digits_pattern(self) -> AnyStr:
        # * This accounts for those cases where a token is used more than once in a rule
        digits_pattern = self._pattern
        for each in list(set(self.fields)):
            regex_pattern = re.compile(each)
            indexes = [match.end() for match in regex_pattern.finditer(digits_pattern)]
            repetetions = len(indexes)
            if repetetions > 1:
                i = 0
                for match in sorted(indexes, reverse=True):
                    digits_pattern = f"{digits_pattern[:match]}{str(repetetions - i)}{digits_pattern[match:]}"
                    i += 1
        return digits_pattern

    @property
    def pattern(self) -> AnyStr:
        return self._pattern

    @property
    def fields(self) -> Tuple:
        """
        Returns:
            [tuple]: Tuple of all Tokens found in this Rule's pattern
        """
        return tuple(self.__FIELDS_REGEX.findall(self._pattern))

    @property
    def regex(self) -> re.Pattern:
        """
        Returns:
            [str]: Regular expression used to parse from this Rule
        """
        return self._regex

    @property
    def name(self) -> AnyStr:
        return self._name

    @name.setter
    def name(self, n: str):
        self._name = n


def add_rule(name: str, pattern: str, anchor=Rule.ANCHOR_START) -> Union[Rule, None]:
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
        Rule: The Rule object instance created for given name and fields. None if
    """
    if pattern == "":
        logger.error(f"Pattern cannot be empty for rule: {name}")
        return
    if name == "":
        logger.error(f"Name cannot be empty for rule: {pattern}")
        return
    if anchor not in [Rule.ANCHOR_START, Rule.ANCHOR_END, Rule.ANCHOR_BOTH]:
        logger.error(f"Invalid anchor value for rule: {name}")
        return
    rule = Rule(name, pattern, anchor)
    _rules[name] = rule
    if get_active_rule() is None:
        set_active_rule(name)
        logger.debug(f"No active rule found, setting this one as active: {name}")
    return rule


def remove_rule(name: AnyStr) -> bool:
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


def has_rule(name: AnyStr) -> bool:
    """Test if current session has a rule with given name.

    Args:
        name (str): The name of the rule to be looked for.

    Returns:
        bool: True if rule with given name exists in current session, False otherwise.
    """
    return name in _rules.keys()


def reset_rules() -> bool:
    """Clears all rules created for current session.

    Returns:
        bool: True if clearing was successful.
    """
    _rules.clear()
    _rules["_active"] = None
    return True


def get_active_rule() -> Rule:
    """Get currently active rule for the session. This is the rule
    that will be used to parse and solve from.

    Returns:
        Rule: Rule object instance for currently active Rule.
    """
    name = _rules.get("_active")
    return _rules.get(name)


def set_active_rule(name: AnyStr) -> bool:
    """Sets given rule as active for the session. This it the rule that's
    being used to parse and solve from.

    Args:
        name (str): The name of the rule to be activated.

    Returns:
        bool: True if successful, False otherwise.
    """
    if has_rule(name):
        _rules["_active"] = name
        return True
    return False


def validate_rule_pattern(name):
    """Validates rule pattern is not empty.

    Args:
        name (str): The name of the rule to validate its pattern.

    Returns:
        bool: True if successful, False otherwise.
    """
    if has_rule(name):
        template_obj = get_rule(name)
        if len(template_obj.pattern) >= 1:
            return True
    return False


def validate_rules():
    not_valid = []
    for name, template in get_rules().items():
        if not validate_rule_pattern(name):
            not_valid.append(name)
    if len(not_valid) >= 1:
        raise RuleError(f"Rules {', '.join(not_valid)}: Patterns are not valid.")


def get_rule(name: AnyStr) -> Rule:
    """Gets Rule object with given name.

    Args:
        name (str): The name of the rule to query.

    Returns:
        Rule: Rule object instance for given name.
    """
    return _rules.get(name)


def get_rules() -> Dict:
    """Get all Rule objects for current session.

    Returns:
        dict: {rule_name:Rule}
    """
    return _rules


def save_rule(name: AnyStr, directory: Path) -> bool:
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
    file_name = f"{name}.rule"
    filepath = directory / file_name
    with open(filepath, "w") as fp:
        json.dump(rule.data(), fp)
    return True


def load_rule(filepath: Path) -> bool:
    """Load rule from given location and create Rule object in memory to work with it.

    Args:
        filepath (str): Path to existing .rule file location

    Returns:
        bool: True if successful, False if .rule wasn't found.
    """
    if not filepath.is_file():
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
