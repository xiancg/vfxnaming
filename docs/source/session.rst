Naming session creation and loading
====================================

Session Creation
----------------

.. code-block:: python

    import vfxnaming as n

    n.add_token('whatAffects')
    n.add_token_number('digits')
    n.add_token('category', natural='nat', 
                practical='pra', dramatic='dra',
                volumetric='vol', default='nat')
    n.add_token('function', key='key', 
                fill='fil', ambient='amb',
                bounce='bnc', rim='rim',
                kick='kik', custom='cst', default='cst')
    n.add_rule(
        'lights',
        '{category}_{function}_{whatAffects}_{digits}_{type}'
    )
    n.save_session()

This will result in the following files being created:

    - lights.rule
    - naming.conf
    - category.token
    - function.token
    - digits.token
    - type.token
    - whatAffects.token

Session Loading
----------------

These files can then be read from next time you need to use your new naming rules by passing
the repo location to the load_session function:

    .. code-block:: python

        import vfxnaming as n

        n.load_session()

        all_rules = n.get_rules()
        all_tokens = n.get_tokens()


Rules with repeated tokens
-----------------------------------------

If your rule uses the same token more than once, then the library will handle it by adding an incremental digit to the token name when parsing and solving.

Here is an example of such a rule being created.

.. code-block:: python

    import vfxnaming as n

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
    rules.add_rule(
        "filename",
        '{side}-{region}_{side}-{region}_{side}-{region}'
    )

    n.save_session()

When **Solving** a name for a rule with repeated tokens you have three options:

1. Explicitly pass each repetition with an added digit for each repetition

.. code-block:: python

    n.solve(
        side1="center", side2="left", side3="right",
        region1="mental", region2="parotidmasseter",
        region3="retromandibularfossa"
    )

2. Explicitly pass some of the repetitions with an added digit for each one. The ones you didn't pass are going to use the token's default.

.. code-block:: python

    n.solve(
        side1="center", side3="right",
        region2="parotidmasseter",
        region3="retromandibularfossa"
    )

3. Explicitly pass just one argument, with no digit added. Your argument will be used for all token repetitions.

.. code-block:: python

    n.solve(
        side="left",
        region1="mental", region2="parotidmasseter",
        region3="retromandibularfossa"
    )

When **Parsing** metadata using a rule with repeated tokens, the dictionary you get back will have the keys for the repeated token altered by an incremental digit at the end of the token name.

.. code-block:: python

    result = {
        "side1": "center", "region1": "frontal",
        "side2": "left", "region2": "orbital",
        "side3": "right", "region3": "zygomatic"
    }

There are many ways to substract that digit from the keys, but maybe the most reliable will be to use regular expressions. You can also use the ``rule.fields`` attribute and compare your keys to the pure token name.

.. code-block:: python

    import re

    pattern = re.compile(r'[a-zA-Z]+')
    for key in result.keys():
        print(pattern.search(key))
