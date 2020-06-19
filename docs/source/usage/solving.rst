Solving
=====================

Solving from a Rule means passing it some parameters and getting back a *name* which follows the Rule's pattern.

.. note::
    The solving function is vfxnaming.solve(args, kwargs)

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

Explicit Vs. Implicit
------------------------

It would not make any sense to make the user pass each and every Token all the time to be able to solve for a name. That'd be the equivalent, almost, to typing the name by hand. Also, it'd be good if the user doesn't have to know all token names by heart (though Rule.fields can help you with that).

That's why vfxnaming.solve() accepts both args and kwargs. Not only that, but if given Token is optional and you want to use it's default value, you don't need to pass it at all.

.. code-block:: python

    n.solve(
        category='natural', function='custom',
        whatAffects='chars', digits=1, type='lighting'
    )
    n.solve(whatAffects='chars', digits=1)
    n.solve('chars', 1)

Each of these calls to vfxnaming.solve() will produce the exact same result:

.. note::
    natural_custom_chars_001_LGT

If you don't pass a required Token (either as an argument or keyword argument), such as 'whatAffects' in this example, you'll get a TokenError.

Solving rules with repeated tokens
-----------------------------------------

If your rule uses the same token more than once, then the library will handle it by adding an incremental digit to the token name when parsing and solving.

Here is an example of such a rule being created.

.. code-block:: python

    import vfxnaming as n

    n.add_token(
        'side', center='C',
        left='L', right='R',
        default='C'
    )
    n.add_token(
        'region', orbital="ORBI",
        parotidmasseter="PAROT", mental="MENT",
        frontal="FRONT", zygomatic="ZYGO",
        retromandibularfossa="RETMAND"
    )
    n.add_rule(
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

2. Explicitly pass some of the repetitions with an added digit for each one. The ones you didn't pass are going to use the Token's default.

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