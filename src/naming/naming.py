# coding=utf-8
'''
Heavily based upon the work of Cesar Saez https://www.cesarsaez.me
'''
from __future__ import absolute_import, print_function

import os
import json
import naming.rules as rules
import naming.tokens as tokens
import naming.separators as separators
from naming.logger import logger

import six

NAMING_REPO_ENV = "NAMING_REPO"


def parse(name):
    rule = rules.get_active_rule()
    return rule.parse(name)


def solve(*args, **kwargs):
    values = dict()
    rule = rules.get_active_rule()
    i = 0
    for f in rule.fields:
        separator = separators.get_separator(f)
        if separator:
            continue
        token = tokens.get_token(f)
        if token:
            # Explicitly passed as keyword argument
            if kwargs.get(f) is not None:
                values[f] = token.solve(kwargs.get(f))
                continue
            elif token.required and kwargs.get(f) is None and len(args) == 0:
                raise Exception("Token {} is required.")
            elif not token.required and kwargs.get(f) is None:
                values[f] = token.solve()
                continue
            # Implicitly passed as positional argument
            try:
                values[f] = token.solve(args[i])
                i += 1
                continue
            except IndexError as why:
                raise IndexError("Missing argument for field '{}'\n{}".format(f, why))
    logger.debug("Solving rule {} with values {}".format(rule.name, values))
    return rule.solve(**values)


def get_repo():
    env_repo = os.environ.get(NAMING_REPO_ENV)
    userPath = os.path.expanduser("~")
    module_dir = os.path.split(__file__)[0]
    config_location = os.path.join(module_dir, "cfg", "config.json")
    config = dict()
    with open(config_location) as fp:
        config = json.load(fp)
    local_repo = os.path.join(userPath, "." + config["logger_dir_name"], "naming_repo")
    result = env_repo or local_repo
    logger.debug("Repo found: {}".format(result))
    return result


def save_session(repo=None):
    repo = repo or get_repo()
    if not os.path.exists(repo):
        os.mkdir(repo)
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
    repo = repo or get_repo()
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
