from attrdict import (
    AttrDict,
)


class AttributeDict(AttrDict):
    def __setitem__(self, attr, val):
        raise TypeError(
            'This data is immutable -- create a copy instead of modifying. '
            'For example, AttributeDict(old, replace_key=replace_val).'
        )
