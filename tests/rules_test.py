import vfxnaming.rules as rules

import pytest


class Test_Rule:
    @pytest.fixture(autouse=True)
    def setup(self):
        rules.reset_rules()

    def test_add(self):
        result = rules.add_rule(
            "lights", "{category}_{function}_{whatAffects}_{digits}_{type}"
        )
        assert isinstance(result, rules.Rule) is True

    def test_reset_rules(self):
        result = rules.reset_rules()
        assert result is True

    def test_remove_rule(self):
        rules.add_rule("test", "{category}_{function}_{digits}_{type}")
        result = rules.remove_rule("test")
        assert result is True

        result = rules.remove_rule("test2")
        assert result is False

    def test_active(self):
        rules.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")
        rules.add_rule("test", "{category}_{function}_{digits}_{type}")
        rules.set_active_rule("test")
        result = rules.get_active_rule()
        assert result is not None
