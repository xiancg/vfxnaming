# coding=utf-8
# MIT License
# Copyright (c) 2017 Cesar Saez and modified by Chris Granados- Xian
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import absolute_import, print_function

import os
import json
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens
import vfxnaming.separators as separators
from vfxnaming.logger import logger
from vfxnaming.error import SolvingError

import six

NAMING_REPO_ENV = "NAMING_REPO"


def parse(name):
    """Get metadata from a name string recognized by the currently active rule.

    -For rules with repeated tokens:

    If your rule uses the same token more than once, the returned dictionary keys
    will have the token name and an incremental digit next to them so they can be
    differentiated.

    Args:
        name (str): Name string e.g.: C_helmet_001_MSH

    Returns:
        dict: A dictionary with keys as tokens and values as given name parts.
        e.g.: {'side':'C', 'part':'helmet', 'number': 1, 'type':'MSH'}
    """
    rule = rules.get_active_rule()
    return rule.parse(name)


def solve(*args, **kwargs):
    """Given arguments are used to build a name following currently active rule.

    -For rules with repeated tokens:

    If your rule uses the same token more than once, pass arguments with the token
    name and add an incremental digit
        i.e.: side1='C', side2='R'

    If your rule uses the same token more than once, you can also pass a single
    instance of the argument and it'll be applied to all repetitions.
        i.e.: side='C'

    If your rule uses the same token more than once, you can ignore one of the repetitions,
    and the solver will use the default value for that token.
        i.e.: side1='C', side4='L'

    Raises:
        SolvingError: A required token was passed as None to keyword arguments.
        SolvingError: Missing argument for one field in currently active rule.

    Returns:
        str: A string with the resulting name.
    """
    rule = rules.get_active_rule()
    # * This accounts for those cases where a token is used more than once in a rule
    repeated_fields = dict()
    for each in rule.fields:
        if each not in separators.get_separators().keys() and each not in repeated_fields.keys():
            if rule.fields.count(each) > 1:
                repeated_fields[each] = 1
    fields_with_digits = list()
    for each in rule.fields:
        if each in repeated_fields.keys():
            counter = repeated_fields.get(each)
            repeated_fields[each] = counter + 1
            field_digit = "{}{}".format(each, counter)
            fields_with_digits.append(field_digit)
        else:
            fields_with_digits.append(each)
    values = dict()
    i = 0
    fields_inc = 0
    for f in fields_with_digits:
        separator = separators.get_separator(f)
        if separator:
            fields_inc += 1
            continue
        token = tokens.get_token(rule.fields[fields_inc])

        if token:
            # Explicitly passed as keyword argument
            if kwargs.get(f) is not None:
                values[f] = token.solve(kwargs.get(f))
                fields_inc += 1
                continue
            # Explicitly passed as keyword argument without repetitive digits
            # Use passed argument for all field repetitions
            elif kwargs.get(rule.fields[fields_inc]) is not None:
                values[f] = token.solve(kwargs.get(rule.fields[fields_inc]))
                fields_inc += 1
                continue
            elif token.required and kwargs.get(f) is None and len(args) == 0:
                raise SolvingError("Token {} is required.")
            # Not required and not passed as keyword argument
            elif not token.required and kwargs.get(f) is None:
                values[f] = token.solve()
                fields_inc += 1
                continue
            # Implicitly passed as positional argument
            try:
                values[f] = token.solve(args[i])
                i += 1
                fields_inc += 1
                continue
            except IndexError as why:
                raise SolvingError("Missing argument for field '{}'\n{}".format(f, why))
    logger.debug("Solving rule {} with values {}".format(rule.name, values))
    return rule.solve(**values)


def get_repo():
    """Get repository location from either global environment variable or local user,
    giving priority to environment variable.

    Environment varialble name: NAMING_REPO

    Returns:
        str: Naming repository location
    """
    env_repo = os.environ.get(NAMING_REPO_ENV)
    userPath = os.path.expanduser("~")
    module_dir = os.path.split(__file__)[0]
    config_location = os.path.join(module_dir, "cfg", "config.json")
    config = dict()
    with open(config_location) as fp:
        config = json.load(fp)
    local_repo = os.path.join(userPath, "." + config["local_repo_name"], "naming_repo")
    result = env_repo or local_repo
    logger.debug("Repo found: {}".format(result))
    return result


def save_session(repo=None):
    """Save rules, tokens, separators and config files to the repository.

    Raises:
        IOError, OSError: Repository directory could not be created.

    Args:
        repo (str, optional): Absolue path to a repository. Defaults to None.

    Returns:
        bool: True if saving session operation was successful.
    """
    repo = repo or get_repo()
    if not os.path.exists(repo):
        try:
            os.mkdir(repo)
        except (IOError, OSError) as why:
            raise why
    # save tokens
    for name, token in six.iteritems(tokens.get_tokens()):
        filepath = os.path.join(repo, name + ".token")
        logger.debug("Saving token: {} in {}".format(name, filepath))
        tokens.save_token(name, filepath)
    # save rules
    for name, rule in six.iteritems(rules.get_rules()):
        if not isinstance(rule, rules.Rule):
            continue
        filepath = os.path.join(repo, name + ".rule")
        logger.debug("Saving rule: {} in {}".format(name, filepath))
        rules.save_rule(name, filepath)
    # save separators
    for name, separator in six.iteritems(separators.get_separators()):
        filepath = os.path.join(repo, name + ".separator")
        logger.debug("Saving separator: {} in {}".format(name, filepath))
        separators.save_separator(name, filepath)
    # extra configuration
    active = rules.get_active_rule()
    config = {"set_active_rule": active.name if active else None}
    filepath = os.path.join(repo, "naming.conf")
    logger.debug("Saving active rule: {} in {}".format(active.name, filepath))
    with open(filepath, "w") as fp:
        json.dump(config, fp, indent=4)
    return True


def load_session(repo=None):
    """Load rules, tokens, separators and config from a repository, and create
    Python objects in memory to work with them.

    Args:
        repo (str, optional): Absolute path to a repository. Defaults to None.

    Returns:
        bool: True if loading session operation was successful.
    """
    repo = repo or get_repo()
    if not os.path.exists(repo):
        logger.warning("Given repo directory does not exist: {}".format(repo))
        return False
    # tokens, rules and separators
    for dirpath, dirnames, filenames in os.walk(repo):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filename.endswith(".token"):
                logger.debug("Loading token: {}".format(filepath))
                tokens.load_token(filepath)
            elif filename.endswith(".rule"):
                logger.debug("Loading rule: {}".format(filepath))
                rules.load_rule(filepath)
            elif filename.endswith(".separator"):
                logger.debug("Loading separator: {}".format(filepath))
                separators.load_separator(filepath)
    # extra configuration
    filepath = os.path.join(repo, "naming.conf")
    if os.path.exists(filepath):
        logger.debug("Loading active rule: {}".format(filepath))
        with open(filepath) as fp:
            config = json.load(fp)
        rules.set_active_rule(config.get('set_active_rule'))
    return True
