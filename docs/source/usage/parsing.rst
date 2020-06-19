Parsing
=====================

Names contain a bunch of metadata about what they are. All of this metadata can be read and used to our advantage. Each Token is basically a piece of metadata. Each Rule helps us extract that metadata from names.

.. note::
    The parsing function is vfxnaming.parse(name)

.. warning::
    The appropiate Rule must be set as active before calling the parse() function. Use vfxnaming.set_active_rule("rule_name")

Let's set these Tokens and Rules.

.. code-block:: python

    import vfxnaming as n

    # CREATE TOKENS
    n.add_token('whatAffects')
    n.add_token_number('digits')
    n.add_token(
        'category',
        natural='nat', practical='pra', dramatic='dra',
        volumetric='vol', default='nat'
    )
    n.add_token(
        'function',
        key='key', fill='fil', ambient='amb',
        bounce='bnc', rim='rim', kick='kik', custom='cst',
        default='cst'
    )
    n.add_token(
        'type', lighting='LGT', animation='ANI', default='LGT'
    )

    # CREATE RULES
    n.add_rule(
        'lights',
        '{category}_{function}_{whatAffects}_{digits}_{type}'
    )

    n.set_active_rule("lights")

And then let's parse this name:

.. code-block:: python

    n.parse("dramatic_bounce_chars_001_LGT")

The result will be the following dictionary with all the metadata extracted to key, value pairs:

.. code-block:: python

    result = {
        "category": "dramatic",
        "function": "bounce",
        "whatAffects": "chars",
        "digits": 1,
        "type":"lighting"
    }

Parsing rules with repeated tokens
-----------------------------------------

If your rule uses the same token more than once, then the library will handle it by adding an incremental digit to the token name when parsing and solving.

Here is an example of such a rule being created.

.. code-block:: python

    import vfxnaming as n

    n.add_token(
        'side',
        center='C', left='L', right='R',
        default='C'
    )
    n.add_token(
        'region',
        orbital="ORBI", parotidmasseter="PAROT", mental="MENT",
        frontal="FRONT", zygomatic="ZYGO", retromandibularfossa="RETMAND"
    )
    n.add_rule(
        "filename",
        '{side}-{region}_{side}-{region}_{side}-{region}'
    )

    n.save_session()

When **Parsing** metadata using a rule with repeated tokens, the dictionary you get back will have the keys for the repeated Token altered by an incremental digit at the end of the token name.

.. code-block:: python

    result = {
        "side1": "center", "region1": "frontal",
        "side2": "left", "region2": "orbital",
        "side3": "right", "region3": "zygomatic"
    }

There are many ways to substract that digit from the keys, but maybe the most reliable could be to use regular expressions. You can also use the ``rule.fields`` attribute and compare your keys to the pure Token name.

.. code-block:: python

    import re

    pattern = re.compile(r'[a-zA-Z]+')
    for key in result.keys():
        print(pattern.search(key))
