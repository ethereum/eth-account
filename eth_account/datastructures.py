from attrdict import (
    AttrDict,
)


class AttributeDict(AttrDict):
    '''
    See `AttrDict docs <https://github.com/bcj/AttrDict#attrdict-1>`_

    This class differs only in that it is made immutable. This immutability
    is **not** a security guarantee. It is only a style-check convenience.
    '''
    def __setitem__(self, attr, val):
        raise TypeError(
            'This data is immutable -- create a copy instead of modifying. '
            'For example, AttributeDict(old, replace_key=replace_val).'
        )

    def _repr_pretty_(self, builder, cycle):
        """
        Custom pretty output for the IPython console
        """
        builder.text(self.__class__.__name__ + "(")
        if cycle:
            builder.text("<cycle>")
        else:
            builder.pretty(dict(self))
        builder.text(")")
