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
import os
import re
import json
import traceback
import shutil
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens
from pathlib import Path
from typing import AnyStr, Dict, Union

from vfxnaming.logger import logger
from vfxnaming.error import SolvingError, RepoError


NAMING_REPO_ENV = "NAMING_REPO"


def parse(name: AnyStr) -> Dict:
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


def solve(*args, **kwargs) -> AnyStr:
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
    rule: rules.Rule = rules.get_active_rule()
    # * This accounts for those cases where a token is used more than once in a rule
    repeated_fields = dict()
    for each in rule.fields:
        if each not in repeated_fields.keys():
            if rule.fields.count(each) > 1:
                repeated_fields[each] = 1
    fields_with_digits = list()
    for each in rule.fields:
        if each in repeated_fields.keys():
            counter = repeated_fields.get(each)
            repeated_fields[each] = counter + 1
            fields_with_digits.append(f"{each}{counter}")
        else:
            fields_with_digits.append(each)
    values = {}
    i = 0
    fields_inc = 0
    for f in fields_with_digits:
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
                if len(token.fallback):
                    values[f] = token.fallback
                    fields_inc += 1
                    continue
                else:
                    raise SolvingError(
                        f"Token {token.name} is required but was not passed."
                    )
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
                raise SolvingError(f"Missing argument for field '{f}'\n{why}")
    logger.debug(f"Solving rule '{rule.name}' with values {values}")
    return rule.solve(**values)


def validate(name: AnyStr, **kwargs) -> bool:
    """Validates a name string against the currently active rule and its
    tokens if passed as keyword arguments.

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

    Args:
        name (str): Name string e.g.: C_helmet_001_MSH

        kwargs (dict): Keyword arguments with token names and values.

    Returns:
        bool: True if the name is valid, False otherwise.
    """
    rule = rules.get_active_rule()
    # * This accounts for those cases where a token is used more than once in a rule
    repeated_fields = dict()
    for each in rule.fields:
        if each not in repeated_fields.keys():
            if rule.fields.count(each) > 1:
                repeated_fields[each] = 1
    fields_with_digits = list()
    for each in rule.fields:
        if each in repeated_fields.keys():
            counter = repeated_fields.get(each)
            repeated_fields[each] = counter + 1
            fields_with_digits.append(f"{each}{counter}")
        else:
            fields_with_digits.append(each)
    values = {}
    fields_inc = 0
    for f in fields_with_digits:
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
            fields_inc += 1
    logger.debug(f"Validating rule '{rule.name}' with values {values}")
    return rule.validate(name, **values)


def validate_repo(repo: Path) -> bool:
    """Valides repo by checking if it contains a vfxnaming.conf file.

    Args:
        repo (Path): Repo dir

    Returns:
        bool: True if valid, False otherwise.
    """
    config_file = repo / "vfxnaming.conf"
    if not config_file.exists():
        return False
    return True


def validate_tokens_and_referenced_rules(pattern: str) -> bool:
    """Validate if the pattern uses tokens and rules that are defined in the current session.

    Args:
        pattern (str): Naming pattern to validate.

    Returns:
        bool: True if successful, False otherwise.
    """
    valid = True

    regex = re.compile(r"{(?P<placeholder>.+?)(:(?P<expression>(\\}|.)+?))?}")
    matches = regex.finditer(pattern)

    all_rules = list(rules.get_rules().keys())
    all_tokens = list(tokens.get_tokens().keys())

    rules_used = []
    tokens_used = []
    for match in matches:
        match_text = match.group(1)
        if match_text.startswith("@"):
            rules_used.append(match_text.replace("@", ""))
        else:
            tokens_used.append(match_text)

    for rule in rules_used:
        if rule not in all_rules:
            valid = False
            break

    for token in tokens_used:
        if token not in all_tokens:
            valid = False
            break

    return valid


def get_repo(force_repo: Union[Path, str] = None) -> Path:
    """Get the path to a folder structures repo.

    Path is looked for in these places and with the given priority:

        1- ``force_repo`` parameter

        2- Environment variable: NAMING_REPO

        3- User config file: C:/Users/xxxxx/.CGXTools/vfxnaming/config.json

        4- Dev config file: __file__/cfg/config.json

    In both config.json files the key it looks for is 'vfxnaming_repo'

    If a root path is passed as ``force_repo`` parameter, then it'll
    return the same path but first checks it actually exists.

    Keyword Arguments:
        ``force_repo`` {Path} -- Use this path instead of looking for
        pre-configured ones (default: {None})

    Raises:
        RepoError: Given repo directory does not exist.

        RepoError: Config file for vfxnmaing library couldn't be found.

    Returns:
        [Path] -- Root path
    """
    # Env level
    env_root = Path(os.environ.get(NAMING_REPO_ENV))

    # User level
    user_cfg_path = Path.expanduser("~") / ".CGXTools/vfxnaming/config.json"
    user_config = {}
    if user_cfg_path.exists():
        with open(user_cfg_path) as fp:
            user_config = json.load(fp)
    user_root = user_config.get("vfxnaming_repo")

    root = env_root or user_root
    if force_repo:
        root = force_repo

    if not validate_repo(root):
        raise RepoError(
            f"VFXNaming repo {root} is not valid, missing vfxnaming.conf file."
        )

    if root.exists():
        logger.debug(f"VFXNaming repo: {root}")
        return root

    raise RepoError(f"VFXNaming repo directory doesn't exist: {root}")


def save_session(repo: Union[Path, None] = None, override=True):
    """Save rules, tokens and config files to the repository.

    Raises:
        RepoError: Repository directory could not be created or is not valid.

        TokenError: Not required tokens must have at least one option (fullname=abbreviation).

        TemplateError: Template patterns are not valid.

    Args:
        ``repo`` (str, optional): Path to a repository. Defaults to None.

        ``override`` (bool, optional): If True, it'll remove given directory and recreate it.

    Returns:
        [bool]: True if saving session operation was successful.
    """
    # Validations
    rules.validate_rules()
    tokens.validate_tokens()

    repo = repo or get_repo()
    if override:
        try:
            shutil.rmtree(repo)
        except (IOError, OSError) as why:
            raise RepoError(why, traceback.format_exc())
    if not repo.exists():
        try:
            os.mkdir(repo)
        except (IOError, OSError) as why:
            raise RepoError(why, traceback.format_exc())

    # Save tokens
    for name, token in tokens.get_tokens().items():
        logger.debug(f"Saving token: {name} in {repo}")
        tokens.save_token(name, repo)
    # Save rules
    for name, template in rules.get_rules().items():
        if not isinstance(template, rules.Rule):
            continue
        logger.debug(f"Saving template: {name} in {repo}")
        rules.save_rule(name, repo)
    # extra configuration
    active = rules.get_active_rule()
    config = {"set_active_rule": active.name if active else None}
    filepath = os.path.join(repo, "vfxnaming.conf")
    logger.debug(f"Saving active rule: {active.name} in {filepath}")
    with open(filepath, "w") as fp:
        json.dump(config, fp, indent=4)
    return True


def load_session(repo: Union[Path, None] = None) -> bool:
    """Load rules, tokens and config from a repository, and create
    Python objects in memory to work with them.

    Args:
        repo (Path, optional): Absolute path to a repository. Defaults to None.

    Returns:
        bool: True if loading session operation was successful.
    """
    repo: Path = repo or get_repo()
    if not repo.exists():
        logger.warning(f"Given repo directory does not exist: {repo}")
        return False
    namingconf = repo / "vfxnaming.conf"
    if not namingconf.exists():
        logger.warning(f"Repo is not valid. vfxnaming.conf not found {namingconf}")
        return False
    rules.reset_rules()
    tokens.reset_tokens()
    # tokens and rules
    for dirpath, dirnames, filenames in os.walk(repo):
        for filename in filenames:
            filepath = Path(dirpath) / filename
            if filename.endswith(".token"):
                logger.debug(f"Loading token: {filepath}")
                tokens.load_token(filepath)
            elif filename.endswith(".rule"):
                logger.debug(f"Loading rule: {filepath}")
                rules.load_rule(filepath)
    # extra configuration
    if namingconf.exists():
        logger.debug(f"Loading active rule: {namingconf}")
        with open(namingconf) as fp:
            config = json.load(fp)
        rules.set_active_rule(config.get("set_active_rule"))
    return True
