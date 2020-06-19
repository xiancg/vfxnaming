Rules module
================

Adding a Rule is as simple as using the ``add_rule()`` function and passing a name and a pattern which uses the Tokens you have created.

The **name** should be unique in the repository.

The **pattern** is a simple string where you place the names of the Tokens you'd like to use inbetween curly brackets and separate them using any of the most commonly separators (hyphen, underscore, dot, etc)

Then there is also the option to use **Anchoring**. This means you can force the evaluation of your Rule to be from left to right (default) or right to left or both. Really useful when you have hardcorded values in your naming Rule. Options for anchoring: Rule.ANCHOR_START (default), Rule.ANCHOR_END, Rule.ANCHOR_BOTH

.. code-block:: python

   import vfxnaming as n

   n.add_rule(
      'lights',
      '{category}_{function}_{whatAffects}_{digits}_{type}'
   )

   n.add_rule(
      'filename',
      '{side}-{region}_{side}-{region}_{side}-{region}'
   )

   n.add_rule(
      'filename',
      'crazy_hardcoded_value_{awesometoken}',
      n.Rule.ANCHOR_END
   )


.. automodule:: vfxnaming.rules
   :members:
