# coding=utf-8
from __future__ import absolute_import, print_function

import copy


class Serializable(object):
    def data(self):
        """Collect all data for this object instance.

        Returns:
            dict: {attribute:value}
        """
        retval = copy.deepcopy(self.__dict__)
        retval["_Serializable_classname"] = type(self).__name__
        retval["_Serializable_version"] = "1.0"
        return retval

    @classmethod
    def from_data(cls, data):
        """Create object instance from give data. Used by Rule,
        Token, Separator to create object instances from disk saved data.

        Args:
            data (dict): {attribute:value}

        Returns:
            Serializable: Object instance for Rule, Token or Separator.
        """
        # Validation
        if data.get("_Serializable_classname") != cls.__name__:
            return None
        del data["_Serializable_classname"]
        if data.get("_Serializable_version") is not None:
            del data["_Serializable_version"]

        this = cls(None)
        this.__dict__.update(data)
        return this
