Validating
=====================

.. note::
    The validating function is vfxnaming.validate(name)

.. warning::
    The appropiate Rule must be set as active before calling the validate() function. Use vfxnaming.set_active_rule("rule_name")

Many times the only thing we need is to know if a name is valid or not for a given rule. Each Rule validates the name according to the next criteria:

- The name must have the same number of tokens as the rule.
- The tokens must be in the same order as the rule.
- The number of expected separators must match with the rule.
- If tokens have options, the given name must use one of those options.
- If token is a number, validates suffix, prefix and padding.

Let's set these Tokens and Rule.

.. code-block:: python

    import vfxnaming as n

    # CREATE TOKENS
    n.reset_tokens()
    n.add_token("whatAffects")
    n.add_token_number("digits")
    n.add_token(
        "category",
        natural="natural",
        practical="practical",
        dramatic="dramatic",
        volumetric="volumetric",
        default="natural",
    )
    n.add_token(
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
    n.add_token("type", lighting="LGT", animation="ANI", default="lighting")

    # CREATE RULES
    n.add_rule("lights", "{category}_{function}_{whatAffects}_{digits}_{type}")

    n.set_active_rule("lights")

And then let's validate these names:

.. code-block:: python

    n.validate("dramatic_bounce_chars_001_LGT")
    # Result: True

    n.validate("dramatic_bounce_chars_001")
    # Result: False. Last token is missing.

    n.validate("whatEver_bounce_chars_001_LGT")
    # Result: False. whatEver is not a valid option for the category token.

    n.validate("dramatic_bounce_chars_01_LGT")
    # Result: False. Padding on numbers by default is 3, got 2 in these case.

    n.validate("dramatic_bounce_chars_v001_LGT")
    # Result: False. No prefix are defined by default or by the code above.
    
    n.validate("dramatic_bounce_chars_1000_LGT")
    # Result: True. Even though 1000 has 4 digits, we're validating padding, not the number of digits.


