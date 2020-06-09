# coding=utf-8
from __future__ import absolute_import, print_function

from vfxnaming import naming as n
import vfxnaming.separators as separators
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens
from vfxnaming import logger
from vfxnaming.error import ParsingError, SolvingError

import pytest
import tempfile

# Debug logging
logger.init_logger()
# logger.init_file_logger()


class Test_Solve:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        tokens.add_token('whatAffects')
        tokens.add_token_number('digits')
        tokens.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        tokens.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        tokens.add_token(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        separators.add_separator('underscore', '_')
        rules.reset_rules()
        rules.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'digits', 'underscore', 'type'
        )

    def test_explicit(self):
        name = 'natural_ambient_chars_001_LGT'
        solved = n.solve(category='natural', function='ambient',
                         whatAffects='chars', digits=1, type='lighting')
        assert solved == name

    def test_no_match_for_token(self):
        with pytest.raises(SolvingError) as exception:
            n.solve(
                category='natural', function='sarasa',
                whatAffects='chars', digits=1, type='lighting'
            )
        assert str(exception.value).startswith("name") is True

    def test_missing_required_token(self):
        with pytest.raises(SolvingError) as exception:
            n.solve(
                category='natural', function='key', digits=1, type='lighting'
            )
        assert str(exception.value).startswith("Token") is True

    def test_missing_not_required_token(self):
        with pytest.raises(SolvingError) as exception:
            n.solve('chars')
        assert str(exception.value).startswith("Missing argument for field") is True

    def test_defaults(self):
        name = 'natural_custom_chars_001_LGT'
        solved = n.solve(category='natural', whatAffects='chars',
                         digits=1, type='lighting')
        assert solved == name

        name = 'natural_custom_chars_001_LGT'
        solved = n.solve(whatAffects='chars', digits=1)
        assert solved == name

    def test_implicit(self):
        name = 'natural_custom_chars_001_ANI'
        solved = n.solve('chars', 1, type='animation')
        assert solved == name

        name = 'natural_custom_chars_001_LGT'
        solved = n.solve('chars', 1)
        assert solved == name


class Test_Parse:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        tokens.add_token('whatAffects')
        tokens.add_token_number('digits')
        tokens.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        tokens.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        tokens.add_token(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )

    def test_parsing_with_separators(self):
        separators.add_separator('underscore', '_')
        rules.reset_rules()
        rules.add_rule(
            'lights',
            'category', 'underscore', 'function', 'underscore', 'whatAffects',
            'underscore', 'digits', 'underscore', 'type'
        )
        name = 'dramatic_bounce_chars_001_LGT'
        parsed = n.parse(name)
        assert parsed['category'] == 'dramatic'
        assert parsed['function'] == 'bounce'
        assert parsed['whatAffects'] == 'chars'
        assert parsed['digits'] == 1
        assert parsed['type'] == 'lighting'

    def test_parsing_without_separators(self):
        rules.reset_rules()
        separators.reset_separators()
        rules.add_rule(
            'lights',
            'category', 'function', 'whatAffects', 'digits', 'type'
        )
        name = 'dramatic_bounce_chars_001_LGT'
        parsed = n.parse(name)
        assert parsed is None


class Test_RuleWithRepetitions:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        rules.reset_rules()
        separators.reset_separators()
        tokens.add_token(
            'side', center='C',
            left='L', right='R',
            default='C'
        )
        tokens.add_token(
            'region', orbital="ORBI",
            parotidmasseter="PAROT", mental="MENT",
            frontal="FRONT", zygomatic="ZYGO",
            retromandibularfossa="RETMAND"
        )
        separators.add_separator('underscore', '_')
        separators.add_separator('hyphen', '-')
        rules.add_rule(
            "filename",
            "side", "hyphen", "region", "underscore",
            "side", "hyphen", "region", "underscore",
            "side", "hyphen", "region"
        )

    def test_parse_repeated_tokens(self):
        name = "C-FRONT_L-ORBI_R-ZYGO"
        expected = {
            "side1": "center", "region1": "frontal",
            "side2": "left", "region2": "orbital",
            "side3": "right", "region3": "zygomatic"
        }
        result = n.parse(name)
        assert result == expected

    def test_parse_repeated_tokens_missing_some(self):
        name = "C-FRONT_-ORBI_R"
        with pytest.raises(ParsingError) as exception:
            n.parse(name)
        assert str(exception.value).startswith("Missing tokens from passed name") is True

    def test_solve_repeated_tokens(self):
        name = "C-MENT_L-PAROT_R-RETMAND"
        result = n.solve(
            side1="center", side2="left", side3="right",
            region1="mental", region2="parotidmasseter",
            region3="retromandibularfossa"
        )

        assert result == name

    def test_solve_repeat_one_token(self):
        name = "L-MENT_L-PAROT_L-RETMAND"
        result = n.solve(
            side="left",
            region1="mental", region2="parotidmasseter",
            region3="retromandibularfossa"
        )

        assert result == name

    def test_solve_repeated_missing_some(self):
        name = "C-FRONT_C-PAROT_R-RETMAND"
        result = n.solve(
            side1="center", side3="right",
            region2="parotidmasseter",
            region3="retromandibularfossa"
        )
        assert result == name


class Test_Serialization:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()
        tokens.reset_tokens()
        separators.reset_separators()

    def test_tokens(self):
        token1 = tokens.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        token2 = tokens.Token.from_data(token1.data())
        assert token1.data() == token2.data()

    def test_rules(self):
        rule1 = rules.add_rule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        rule2 = rules.Rule.from_data(rule1.data())
        assert rule1.data() == rule2.data()

    def test_separators(self):
        separator1 = separators.add_separator('underscore', '_')
        separator2 = separators.Separator.from_data(separator1.data())
        assert separator1.data() == separator2.data()

    def test_validation(self):
        token = tokens.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        rule = rules.add_rule(
            'lights', 'category', 'function', 'whatAffects', 'digits', 'type'
            )
        token_number = tokens.add_token_number('digits')
        sep = separators.add_separator('dot', '.')

        assert rules.Rule.from_data(token.data()) is None
        assert tokens.Token.from_data(rule.data()) is None
        assert tokens.TokenNumber.from_data(sep.data()) is None
        assert separators.Separator.from_data(token_number.data()) is None

    def test_save_load_rule(self):
        rules.add_rule('test', 'category', 'function', 'whatAffects', 'digits', 'type')
        filepath = tempfile.mktemp()
        rules.save_rule('test', filepath)

        rules.reset_rules()
        rules.load_rule(filepath)
        assert rules.has_rule('test') is True

    def test_save_load_token(self):
        tokens.add_token(
            'test', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        filepath = tempfile.mktemp()
        tokens.save_token('test', filepath)

        tokens.reset_tokens()
        tokens.load_token(filepath)
        assert tokens.has_token('test') is True

    def test_save_load_token_number(self):
        tokens.add_token_number('test')
        filepath = tempfile.mktemp()
        tokens.save_token('test', filepath)

        tokens.reset_tokens()
        tokens.load_token(filepath)
        assert tokens.has_token('test') is True

    def test_save_load_separator(self):
        separators.add_separator('test')
        filepath = tempfile.mktemp()
        separators.save_separator('test', filepath)

        separators.reset_separators()
        separators.load_separator(filepath)
        assert separators.has_separator('test') is True

    def test_save_load_session(self):
        tokens.add_token('whatAffects')
        tokens.add_token_number('digits')
        tokens.add_token(
            'category', natural='natural',
            practical='practical', dramatic='dramatic',
            volumetric='volumetric', default='natural'
            )
        tokens.add_token(
            'function', key='key',
            fill='fill', ambient='ambient',
            bounce='bounce', rim='rim',
            kick='kick', default='custom'
            )
        tokens.add_token(
            'type', lighting='LGT',
            animation='ANI', default='LGT'
            )
        separators.add_separator('dot', '.')
        separators.add_separator('underscore', '.')
        rules.add_rule(
            'lights',
            'category', 'dot', 'function', 'dot', 'whatAffects',
            'underscore', 'digits', 'dot', 'type'
        )
        rules.add_rule(
            'test', 'category', 'underscore', 'function'
        )
        rules.set_active_rule('lights')

        repo = tempfile.mkdtemp()
        save_result = n.save_session(repo)
        assert save_result is True

        rules.reset_rules()
        tokens.reset_tokens()
        separators.reset_separators()

        n.load_session(repo)
        assert tokens.has_token('whatAffects') is True
        assert tokens.has_token('digits') is True
        assert tokens.has_token('category') is True
        assert tokens.has_token('function') is True
        assert tokens.has_token('type') is True
        assert rules.has_rule('lights') is True
        assert rules.has_rule('test') is True
        assert separators.has_separator('underscore') is True
        assert separators.has_separator('dot') is True
        assert rules.get_active_rule().name == 'lights'
