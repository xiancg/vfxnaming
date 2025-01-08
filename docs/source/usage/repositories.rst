Naming Repository creation and loading
=======================================

Using **vfxnaming** means basically creating a series of Tokens and Rules that then get saved to a repository (a simple folder with some files in it).

The saved files are the serialized objects in JSON format, which has the huge advantage of being interchangeable with practically any other programming language.

1.Repo Creation Session
------------------------------

.. code-block:: python
    :linenos:

    import vfxnaming as n

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
    n.add_rule(
        'lights',
        '{category}_{function}_{whatAffects}_{digits}_{type}'
    )
    my_repo = 'C:/path/to/my/repo'
    n.save_session(my_repo)

This will result in the following files being created:

    - lights.rule
    - naming.conf
    - category.token
    - function.token
    - digits.token
    - type.token
    - whatAffects.token

If there is only one rule, it'll be set as active by default. If there is more than one, you need to activate that template before using parsing or solving.

When saving the session, all Tokens and Rules in memory will be saved to the repository along with a naming.conf file that stores the last active Rule (It'll be set as active again when loading the session from the repo next time.)

1.1 Adding Tokens
------------------------------

.. code-block:: python
    :linenos:

    n.add_token('whatAffects')
    n.add_token('shadowType', fallback='soft')
    n.add_token_number('digits')
    n.add_token(
        'category',
        natural='nat', practical='pra', dramatic='dra',
        volumetric='vol', default='nat'
    )

In line 1 we're creating a **Required Token**. This means that in order to solve the user must provide a value, else an error will be raised. This is a explicit solve.

In line 2 we're creating a **Required Token** with a fallback. This means that if the user doesn't provide a value, the Token will solve to the fallback value. This is an implicit solve.

In line 3 we're creating a **Number Token**. This is a special Token really useful for working with version like or counting parts of a name. It's always required.

In line 4 we're creating an **Optional Token**, which means that for solving the user can pass one of the options in the Token or simply ignore passing a value and the Token will solve to it's default option. This is an implicit solve, which helps to greatly reduce the amount of info that needs to be passed to solve for certain cases.

For more information on implicit and explicit solving please check :doc:`solving`

1.2 Adding Rules
--------------------------------

.. code-block:: python
    :linenos:

    n.add_rule(
        'lights',
        '{category}_{function}_{whatAffects}_{digits}_{type}'
    )

    n.add_rule(
        'filename',
        'crazy_hardcoded_value_{awesometoken}',
        n.Rule.ANCHOR_END
    )

Here we're creating naming rules, giving them a name, a pattern and an anchor optionally. *Name must be unique* for each rule in the repo.

*Patterns* must be structured so that each Token is identified by it's name and enclosed between curly brackets '{ }'.

**Anchoring** means you can force the evaluation of your Rule to be from left to right (default) or right to left or both. Really useful when you have hardcorded values in your naming Rule. Options for anchoring: Rule.ANCHOR_START (default), Rule.ANCHOR_END, Rule.ANCHOR_BOTH

2. Repo Loading Session
--------------------------------

These files can then be read from next time you need to use your new naming rules by passing
the repo location to the load_session function. Python object instances will be loaded into memory and you'll be able to interact with them (solving, parsing, adding new rules, new tokens, etc):

    .. code-block:: python

        import vfxnaming as n

        my_repo = 'C:/path/to/my/repo'
        n.load_session(my_repo)

        all_rules = n.get_rules()
        all_tokens = n.get_tokens()

.. warning::
    It's important to manipulate both Tokens and Rules through their module functions, not the object methods. This is so the system can keep track of what's created, removed, updated, etc, during the repo creation session.