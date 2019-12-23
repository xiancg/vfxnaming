# coding=utf-8
from __future__ import absolute_import, print_function

from cgx_naming.naming import parse, solve, get_repo, save_session, load_session
from cgx_naming.rules import add_rule, add_template_rule, remove_rule, has_rule, reset_rules, get_active_rule, set_active_rule, get_rule, get_rules, save_rule, load_rule
from cgx_naming.tokens import add_token, add_token_number, remove_token, has_token, reset_tokens, get_token, get_tokens, save_token, load_token
from cgx_naming.separators import add_separator, remove_separator, has_separator, reset_separators, get_separator, get_separators, save_separator, load_separator
