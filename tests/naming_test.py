from vfxnaming import naming as n
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens
from vfxnaming.error import ParsingError, SolvingError, TokenError

import os
import pytest
import tempfile


class Test_Solve:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        tokens.add_token("whatAffects")
        tokens.add_token_number("digits")
        tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )
        tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            custom="custom",
            kick="kick",
            default="custom",
        )
        tokens.add_token("type", lighting="LGT", animation="ANI", default="lighting")
        rules.reset_rules()
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")

    def test_explicit(self):
        name = "natural_ambient_chars_001_LGT"
        solved = n.solve(
            category="natural",
            function="ambient",
            whatAffects="chars",
            digits=1,
            type="lighting",
        )
        assert solved == name

    def test_no_match_for_token(self):
        with pytest.raises(TokenError) as exception:
            n.solve(
                category="natural",
                function="sarasa",
                whatAffects="chars",
                digits=1,
                type="lighting",
            )
        assert str(exception.value).startswith("name") is True

    def test_missing_required_token(self):
        with pytest.raises(SolvingError) as exception:
            n.solve(category="natural", function="key", digits=1, type="lighting")
        assert str(exception.value).startswith("Token") is True

    def test_missing_not_required_token(self):
        with pytest.raises(SolvingError) as exception:
            n.solve("chars")
        assert str(exception.value).startswith("Missing argument for field") is True

    def test_defaults(self):
        name = "natural_custom_chars_001_LGT"
        solved = n.solve(
            category="natural", whatAffects="chars", digits=1, type="lighting"
        )
        assert solved == name

        name = "natural_custom_chars_001_LGT"
        solved = n.solve(whatAffects="chars", digits=1)
        assert solved == name

    def test_implicit(self):
        name = "natural_custom_chars_001_ANI"
        solved = n.solve("chars", 1, type="animation")
        assert solved == name

        name = "natural_custom_chars_001_LGT"
        solved = n.solve("chars", 1)
        assert solved == name


class Test_Parse:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        tokens.add_token("whatAffects")
        tokens.add_token_number("digits")
        tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )
        tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            custom="custom",
            kick="kick",
            default="custom",
        )
        tokens.add_token("type", lighting="LGT", animation="ANI", default="lighting")

    def test_parsing_with_separators(self):
        rules.reset_rules()
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")
        name = "dramatic_bounce_chars_001_LGT"
        parsed = n.parse(name)
        assert parsed["category"] == "dramatic"
        assert parsed["function"] == "bounce"
        assert parsed["whatAffects"] == "chars"
        assert parsed["digits"] == 1
        assert parsed["type"] == "lighting"

    def test_parsing_without_separators(self):
        rules.reset_rules()
        rules.add_rule("lights", "{category}{function}{whatAffects}{digits}{type}")
        name = "dramatic_bounce_chars_001_LGT"
        parsed = n.parse(name)
        assert parsed is None


class Test_RuleWithRepetitions:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        rules.reset_rules()
        tokens.add_token("side", center="C", left="L", right="R", default="center")
        tokens.add_token(
            "region",
            orbital="ORBI",
            parotidmasseter="PAROT",
            mental="MENT",
            frontal="FRONT",
            zygomatic="ZYGO",
            retromandibularfossa="RETMAND",
        )
        rules.add_rule("filename", "{side}-{region}_{side}-{region}_{side}-{region}")

    def test_parse_repeated_tokens(self):
        name = "C-FRONT_L-ORBI_R-ZYGO"
        expected = {
            "side1": "center",
            "region1": "frontal",
            "side2": "left",
            "region2": "orbital",
            "side3": "right",
            "region3": "zygomatic",
        }
        result = n.parse(name)
        assert result == expected

    def test_parse_repeated_tokens_missing_some(self):
        name = "C-FRONT_-ORBI_R"
        with pytest.raises(ParsingError) as exception:
            n.parse(name)
        assert str(exception.value).startswith("Separators count mismatch") is True

    def test_solve_repeated_tokens(self):
        name = "C-MENT_L-PAROT_R-RETMAND"
        result = n.solve(
            side1="center",
            side2="left",
            side3="right",
            region1="mental",
            region2="parotidmasseter",
            region3="retromandibularfossa",
        )

        assert result == name

    def test_solve_repeat_one_token(self):
        name = "L-MENT_L-PAROT_L-RETMAND"
        result = n.solve(
            side="left",
            region1="mental",
            region2="parotidmasseter",
            region3="retromandibularfossa",
        )

        assert result == name

    def test_solve_repeated_missing_some(self):
        name = "C-FRONT_C-PAROT_R-RETMAND"
        result = n.solve(
            side1="center",
            side3="right",
            region2="parotidmasseter",
            region3="retromandibularfossa",
        )
        assert result == name


class Test_Anchoring:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        tokens.add_token("awesometoken")

    def test_solve_anchoring_end(self):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "crazy_hardcoded_value_{awesometoken}", rules.Rule.ANCHOR_END
        )

        name = "crazy_hardcoded_value_bye"
        solved = n.solve("bye")
        assert solved == name

    def test_solve_anchoring_both(self):
        rules.reset_rules()
        rules.add_rule(
            "anchoring",
            "{awesometoken}_crazy_hardcoded_value_{awesometoken}",
            rules.Rule.ANCHOR_BOTH,
        )

        name = "hello_crazy_hardcoded_value_bye"
        solved = n.solve(awesometoken1="hello", awesometoken2="bye")
        assert solved == name

    def test_solve_anchoring_start(self):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "{awesometoken}_crazy_hardcoded_value", rules.Rule.ANCHOR_START
        )

        name = "hello_crazy_hardcoded_value"
        solved = n.solve(awesometoken="hello")
        assert solved == name

    def test_parse_anchoring_end(self):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "crazy_hardcoded_value_{awesometoken}", rules.Rule.ANCHOR_END
        )

        name = "crazy_hardcoded_value_bye"
        parsed = n.parse(name)
        assert parsed == {"awesometoken": "bye"}

    def test_parse_anchoring_both(self):
        rules.reset_rules()
        rules.add_rule(
            "anchoring",
            "{awesometoken}_crazy_hardcoded_value_{awesometoken}",
            rules.Rule.ANCHOR_BOTH,
        )

        name = "hello_crazy_hardcoded_value_bye"
        parsed = n.parse(name)
        assert parsed == {"awesometoken1": "hello", "awesometoken2": "bye"}

    def test_parse_anchoring_start(self):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "{awesometoken}_crazy_hardcoded_value", rules.Rule.ANCHOR_START
        )

        name = "hello_crazy_hardcoded_value"
        parsed = n.parse(name)
        assert parsed == {"awesometoken": "hello"}


class Test_Serialization:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()
        tokens.reset_tokens()

    def test_tokens(self):
        token1 = tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            custom="custom",
            kick="kick",
            default="custom",
        )
        token2 = tokens.Token.from_data(token1.data())
        assert token1.data() == token2.data()

    def test_rules(self):
        rule1 = rules.add_rule(
            "lights", "{category}_{function}_{whatAffects}_{digits}_{type}"
        )
        rule2 = rules.Rule.from_data(rule1.data())
        assert rule1.data() == rule2.data()

    def test_validation(self):
        token = tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            custom="custom",
            kick="kick",
            default="custom",
        )
        rule = rules.add_rule(
            "lights", "{category}_{function}_{whatAffects}_{digits}_{type}"
        )
        tokens.add_token_number("digits")

        assert rules.Rule.from_data(token.data()) is None
        assert tokens.Token.from_data(rule.data()) is None

    def test_save_load_rule(self):
        rules.add_rule("test", "{category}_{function}_{whatAffects}_{digits}_{type}")
        tempdir = tempfile.mkdtemp()
        rules.save_rule("test", tempdir)

        rules.reset_rules()
        file_name = "test.rule"
        filepath = os.path.join(tempdir, file_name)
        rules.load_rule(filepath)
        assert rules.has_rule("test") is True

    def test_save_load_token(self):
        tokens.add_token(
            "test",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            custom="custom",
            kick="kick",
            default="custom",
        )
        tempdir = tempfile.mkdtemp()
        tokens.save_token("test", tempdir)

        tokens.reset_tokens()
        file_name = "test.token"
        filepath = os.path.join(tempdir, file_name)
        tokens.load_token(filepath)
        assert tokens.has_token("test") is True

    def test_save_load_token_number(self):
        tokens.add_token_number("test")
        tempdir = tempfile.mkdtemp()
        tokens.save_token("test", tempdir)

        tokens.reset_tokens()
        file_name = "test.token"
        filepath = os.path.join(tempdir, file_name)
        tokens.load_token(filepath)
        assert tokens.has_token("test") is True

    def test_save_load_session(self):
        tokens.add_token("whatAffects")
        tokens.add_token_number("digits")
        tokens.add_token(
            "category",
            natural="natural",
            practical="practical",
            dramatic="dramatic",
            volumetric="volumetric",
            default="natural",
        )
        tokens.add_token(
            "function",
            key="key",
            fill="fill",
            ambient="ambient",
            bounce="bounce",
            rim="rim",
            custom="custom",
            kick="kick",
            default="custom",
        )
        tokens.add_token("type", lighting="LGT", animation="ANI", default="lighting")
        rules.add_rule("lights", "{category}.{function}.{whatAffects}.{digits}.{type}")
        rules.add_rule("test", "{category}_{function}")
        rules.set_active_rule("lights")

        repo = tempfile.mkdtemp()
        save_result = n.save_session(repo)
        assert save_result is True

        rules.reset_rules()
        tokens.reset_tokens()

        n.load_session(repo)
        assert tokens.has_token("whatAffects") is True
        assert tokens.has_token("digits") is True
        assert tokens.has_token("category") is True
        assert tokens.has_token("function") is True
        assert tokens.has_token("type") is True
        assert rules.has_rule("lights") is True
        assert rules.has_rule("test") is True
        assert rules.get_active_rule().name == "lights"
