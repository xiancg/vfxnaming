from pathlib import Path
import pytest
import tempfile
from typing import Dict, List

from vfxnaming import naming as n
import vfxnaming.rules as rules
import vfxnaming.tokens as tokens
from vfxnaming.error import ParsingError, SolvingError, TokenError


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

    @pytest.mark.parametrize(
        "name,solve_data,expected",
        [
            (
                "natural_ambient_chars_001_LGT",
                {
                    "category": "natural",
                    "function": "ambient",
                    "whatAffects": "chars",
                    "digits": 1,
                    "type": "lighting",
                },
                True,
            ),
            (
                "natural_key_env_010_LGT",
                {
                    "category": "natural",
                    "function": "ambient",
                    "whatAffects": "chars",
                    "digits": 1,
                    "type": "lighting",
                },
                False,
            ),
        ],
    )
    def test_explicit(self, name: str, solve_data: Dict, expected: bool):
        solved = n.solve(**solve_data)
        assert (solved == name) is expected

    def test_no_match_for_token(self):
        with pytest.raises(TokenError):
            n.solve(
                category="natural",
                function="whatever",
                whatAffects="chars",
                digits=1,
                type="lighting",
            )

    def test_missing_required_token(self):
        with pytest.raises(SolvingError):
            n.solve(category="natural", function="key", digits=1, type="lighting")

    def test_missing_not_required_token(self):
        with pytest.raises(SolvingError):
            n.solve("chars")

    @pytest.mark.parametrize(
        "name,solve_data,expected",
        [
            (
                "natural_custom_chars_001_LGT",
                {
                    "category": "natural",
                    "whatAffects": "chars",
                    "digits": 1,
                    "type": "lighting",
                },
                True,
            ),
            (
                "natural_custom_chars_001_LGT",
                {"whatAffects": "chars", "digits": 1},
                True,
            ),
            (
                "whatever_nondefault_chars_001_LGT",
                {"whatAffects": "chars", "digits": 1},
                False,
            ),
        ],
    )
    def test_defaults(self, name: str, solve_data: Dict, expected: bool):
        solved = n.solve(**solve_data)
        assert (solved == name) is expected

    @pytest.mark.parametrize(
        "name,solve_args,solve_kwargs",
        [
            (
                "natural_custom_chars_001_ANI",
                ["chars", 1],
                {"type": "animation"},
            ),
            (
                "natural_custom_chars_001_LGT",
                ["chars", 1],
                {},
            ),
        ],
    )
    def test_implicit(self, name: str, solve_args: List, solve_kwargs: Dict):
        solved = n.solve(*solve_args, **solve_kwargs)
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

    @pytest.mark.parametrize(
        "name,parsed_data",
        [
            (
                "dramatic_bounce_chars_001_LGT",
                {
                    "category": "dramatic",
                    "function": "bounce",
                    "whatAffects": "chars",
                    "digits": 1,
                    "type": "lighting",
                },
            ),
            (
                "natural_key_env_012_ANI",
                {
                    "category": "natural",
                    "function": "key",
                    "whatAffects": "env",
                    "digits": 12,
                    "type": "animation",
                },
            ),
        ],
    )
    def test_parsing_with_separators(self, name: str, parsed_data: Dict):
        rules.reset_rules()
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")
        parsed = n.parse(name)
        for key, value in parsed_data.items():
            assert parsed.get(key) == value

    def test_parsing_without_separators(self):
        rules.reset_rules()
        rules.add_rule("lights", "{category}{function}{whatAffects}{digits}{type}")
        name = "dramatic_bounce_chars_001_LGT"
        parsed = n.parse(name)
        assert parsed is None


class Test_Validate:
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
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")
        rules.add_rule(
            "lights_extra",
            "With_extra_{category}_{function}_{whatAffects}_{digits}_{type}",
        )

    @pytest.mark.parametrize(
        "name,expected",
        [
            (
                "dramatic_bounce_chars_001_LGT",
                1,
            ),
            (
                "dramatic_bounce_chars_001",
                0,
            ),
            (
                "whatEver_bounce_chars_001_LGT",
                0,
            ),
            (
                "dramatic_bounce_chars_01_LGT",
                0,
            ),
            (
                "dramatic_bounce_chars_v001_LGT",
                0,
            ),
            (
                "dramatic_bounce_chars_1000_LGT",
                1,
            ),
        ],
    )
    def test_valid(self, name: str, expected: int):
        rules.set_active_rule("lights")
        validated = n.validate(name)
        assert len(validated) == expected

    @pytest.mark.parametrize(
        "name,validate_values,expected",
        [
            (
                "dramatic_bounce_chars_001_LGT",
                {"category": "dramatic"},
                1,
            ),
            (
                "dramatic_bounce_chars_001_LGT",
                {"whatAffects": "chars"},
                1,
            ),
            (
                "dramatic_bounce_chars_001_LGT",
                {"category": "practical"},
                0,
            ),
            (
                "dramatic_bounce_chars_001_LGT",
                {"whatAffects": "anything"},
                0,
            ),
        ],
    )
    def test_valid_with_tokens(self, name: str, validate_values: dict, expected: int):
        rules.set_active_rule("lights")
        validated = n.validate(name, **validate_values)
        assert len(validated) == expected

    @pytest.mark.parametrize(
        "name,expected",
        [
            (
                "With_extra_dramatic_bounce_chars_001_LGT",
                1,
            ),
            (
                "Withextra_dramatic_bounce_chars_001_LGT",
                0,
            ),
        ],
    )
    def test_valid_with_hardcoded(self, name: str, expected: int):
        rules.set_active_rule("lights_extra")
        validated = n.validate(name)
        assert len(validated) == expected


class Test_ValidateHarcodedValues:
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
        rules.add_rule("filename", "{side}-ALWAYS_{side}-This_{side}-{region}")

    @pytest.mark.parametrize(
        "name,strict,expected",
        [
            ("C-ALWAYS_C-This_C-ORBI", False, 1),
            ("C-always_C-This_C-ORBI", False, 1),
            ("C-always_C-this_C-ORBI", True, 0),
        ],
    )
    def test_valid_harcoded(self, name: str, strict: bool, expected: int):
        validated = n.validate(name, strict=strict)
        assert len(validated) == expected


class Test_ValidateWithRepetitions:
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

    @pytest.mark.parametrize(
        "name,validate_values,expected",
        [
            (
                "C-FRONT_L-ORBI_R-ZYGO",
                {
                    "side1": "center",
                    "region1": "frontal",
                    "side2": "left",
                    "region2": "orbital",
                    "side3": "right",
                    "region3": "zygomatic",
                },
                1,
            ),
            (
                "R-MENT_C-PAROT_L-RETMAND",
                {
                    "side2": "center",
                },
                1,
            ),
            (
                "R-MENT_C-PAROT_L-RETMAND",
                {
                    "side": "center",
                },
                0,
            ),
        ],
    )
    def test_valid_with_repetitions(
        self, name: str, validate_values: dict, expected: int
    ):
        validated = n.validate(name, **validate_values)
        assert len(validated) == expected


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

    @pytest.mark.parametrize(
        "name,expected",
        [
            (
                "C-FRONT_L-ORBI_R-ZYGO",
                {
                    "side1": "center",
                    "region1": "frontal",
                    "side2": "left",
                    "region2": "orbital",
                    "side3": "right",
                    "region3": "zygomatic",
                },
            ),
            (
                "R-MENT_C-PAROT_L-RETMAND",
                {
                    "side1": "right",
                    "region1": "mental",
                    "side2": "center",
                    "region2": "parotidmasseter",
                    "side3": "left",
                    "region3": "retromandibularfossa",
                },
            ),
        ],
    )
    def test_parse_repeated_tokens(self, name: str, expected: Dict):
        result = n.parse(name)
        assert result == expected

    def test_parse_repeated_tokens_missing_some(self):
        name = "C-FRONT_-ORBI_R"
        with pytest.raises(ParsingError):
            n.parse(name)

    @pytest.mark.parametrize(
        "name,data",
        [
            (
                "C-MENT_L-PAROT_R-RETMAND",
                {
                    "side1": "center",
                    "side2": "left",
                    "side3": "right",
                    "region1": "mental",
                    "region2": "parotidmasseter",
                    "region3": "retromandibularfossa",
                },
            ),
            (
                "C-FRONT_R-ORBI_L-ZYGO",
                {
                    "side1": "center",
                    "side2": "right",
                    "side3": "left",
                    "region1": "frontal",
                    "region2": "orbital",
                    "region3": "zygomatic",
                },
            ),
        ],
    )
    def test_solve_repeated_tokens(self, name: str, data: Dict):
        result = n.solve(**data)
        assert result == name

    @pytest.mark.parametrize(
        "name,data",
        [
            (
                "L-MENT_L-PAROT_L-RETMAND",
                {
                    "side": "left",
                    "region1": "mental",
                    "region2": "parotidmasseter",
                    "region3": "retromandibularfossa",
                },
            ),
            (
                "R-FRONT_R-FRONT_R-FRONT",
                {
                    "side1": "right",
                    "side2": "right",
                    "side3": "right",
                    "region": "frontal",
                },
            ),
        ],
    )
    def test_solve_repeat_one_token(self, name: str, data: Dict):
        result = n.solve(**data)
        assert result == name

    @pytest.mark.parametrize(
        "name,data",
        [
            (
                "C-ORBI_C-PAROT_R-RETMAND",
                {
                    "side3": "right",
                    "region2": "parotidmasseter",
                    "region3": "retromandibularfossa",
                },
            ),
            (
                "L-ORBI_C-RETMAND_R-ORBI",
                {
                    "side1": "left",
                    "side3": "right",
                    "region2": "retromandibularfossa",
                },
            ),
        ],
    )
    def test_solve_repeated_missing_some(self, name: str, data: Dict):
        result = n.solve(**data)
        assert result == name


class Test_Anchoring:
    @pytest.fixture(autouse=True)
    def setup(self):
        tokens.reset_tokens()
        tokens.add_token("awesometoken")

    @pytest.mark.parametrize(
        "anchor_position,expected",
        [
            (rules.Rule.ANCHOR_END, True),
            (rules.Rule.ANCHOR_BOTH, True),
            (rules.Rule.ANCHOR_START, True),
        ],
    )
    def test_solve_anchoring_end(self, anchor_position: int, expected: bool):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "crazy_hardcoded_value_{awesometoken}", anchor_position
        )
        name = "crazy_hardcoded_value_bye"
        solved = n.solve("bye")
        assert (solved == name) is expected

    @pytest.mark.parametrize(
        "anchor_position,expected",
        [
            (rules.Rule.ANCHOR_END, True),
            (rules.Rule.ANCHOR_BOTH, True),
            (rules.Rule.ANCHOR_START, True),
        ],
    )
    def test_solve_anchoring_both(self, anchor_position: int, expected: bool):
        rules.reset_rules()
        rules.add_rule(
            "anchoring",
            "{awesometoken}_crazy_hardcoded_value_{awesometoken}",
            anchor_position,
        )

        name = "hello_crazy_hardcoded_value_bye"
        solved = n.solve(awesometoken1="hello", awesometoken2="bye")
        assert (solved == name) is expected

    @pytest.mark.parametrize(
        "anchor_position,expected",
        [
            (rules.Rule.ANCHOR_END, True),
            (rules.Rule.ANCHOR_BOTH, True),
            (rules.Rule.ANCHOR_START, True),
        ],
    )
    def test_solve_anchoring_start(self, anchor_position: int, expected: bool):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "{awesometoken}_crazy_hardcoded_value", anchor_position
        )

        name = "hello_crazy_hardcoded_value"
        solved = n.solve(awesometoken="hello")
        assert (solved == name) is expected

    @pytest.mark.parametrize(
        "anchor_position,expected",
        [
            (rules.Rule.ANCHOR_END, True),
            (rules.Rule.ANCHOR_BOTH, True),
            (rules.Rule.ANCHOR_START, True),
        ],
    )
    def test_parse_anchoring_end(self, anchor_position: int, expected: bool):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "crazy_hardcoded_value_{awesometoken}", anchor_position
        )

        name = "crazy_hardcoded_value_bye"
        parsed = n.parse(name)
        assert (parsed == {"awesometoken": "bye"}) is expected

    @pytest.mark.parametrize(
        "anchor_position,expected",
        [
            (rules.Rule.ANCHOR_END, True),
            (rules.Rule.ANCHOR_BOTH, True),
            (rules.Rule.ANCHOR_START, True),
        ],
    )
    def test_parse_anchoring_both(self, anchor_position: int, expected: bool):
        rules.reset_rules()
        rules.add_rule(
            "anchoring",
            "{awesometoken}_crazy_hardcoded_value_{awesometoken}",
            anchor_position,
        )

        name = "hello_crazy_hardcoded_value_bye"
        parsed = n.parse(name)
        assert (parsed == {"awesometoken1": "hello", "awesometoken2": "bye"}) is expected

    @pytest.mark.parametrize(
        "anchor_position,expected",
        [
            (rules.Rule.ANCHOR_END, True),
            (rules.Rule.ANCHOR_BOTH, True),
            (rules.Rule.ANCHOR_START, True),
        ],
    )
    def test_parse_anchoring_start(self, anchor_position: int, expected: bool):
        rules.reset_rules()
        rules.add_rule(
            "anchoring", "{awesometoken}_crazy_hardcoded_value", anchor_position
        )

        name = "hello_crazy_hardcoded_value"
        parsed = n.parse(name)
        assert (parsed == {"awesometoken": "hello"}) is expected


class Test_Serialization:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()
        tokens.reset_tokens()

    @pytest.mark.parametrize(
        "name,options",
        [
            (
                "function",
                {
                    "key": "key",
                    "fill": "fill",
                    "ambient": "ambient",
                    "bounce": "bounce",
                    "rim": "rim",
                    "custom": "custom",
                    "kick": "kick",
                    "default": "custom",
                },
            ),
            (
                "side",
                {
                    "left": "left",
                    "right": "right",
                    "center": "center",
                },
            ),
        ],
    )
    def test_tokens(self, name: str, options: Dict):
        token1 = tokens.add_token(name, **options)
        token2 = tokens.Token.from_data(token1.data())
        assert token1.data() == token2.data()

    @pytest.mark.parametrize(
        "name,pattern",
        [
            (
                "lights",
                "{category}_{function}_{whatAffects}_{digits}_{type}",
            ),
            (
                "filename",
                "{side}-{region}_{side}-{region}_{side}-{region}",
            ),
        ],
    )
    def test_rules(self, name: str, pattern: str):
        rule1 = rules.add_rule(name, pattern)
        rule2 = rules.Rule.from_data(rule1.data())
        assert rule1.data() == rule2.data()

    def test_from_data_validation(self):
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
        tempdir = Path(tempfile.mkdtemp())
        rules.save_rule("test", tempdir)

        rules.reset_rules()
        file_name = "test.rule"
        filepath = tempdir / file_name
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
        tempdir = Path(tempfile.mkdtemp())
        tokens.save_token("test", tempdir)

        tokens.reset_tokens()
        file_name = "test.token"
        filepath = tempdir / file_name
        tokens.load_token(filepath)
        assert tokens.has_token("test") is True

    def test_save_load_token_number(self):
        tokens.add_token_number("test")
        tempdir = Path(tempfile.mkdtemp())
        tokens.save_token("test", tempdir)

        tokens.reset_tokens()
        file_name = "test.token"
        filepath = tempdir / file_name
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

        repo = Path(tempfile.mkdtemp())
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
