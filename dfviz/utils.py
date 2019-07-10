import logging
logger = logging.getLogger('dfviz')


def pretty_describe(object, nestedness=0, indent=2):
    """Nice YAML-like text version of given dict/object

    Maintains dict ordering
    """
    if not isinstance(object, dict):
        return str(object)
    sep = '\n{}'.format(" " * nestedness * indent)
    out = sep.join(('{}: {}'.format(k, pretty_describe(v, nestedness + 1))
                    for k, v in object.items()))
    if nestedness > 0 and out:
        return '{sep}{out}'.format(sep=sep, format=format)
    return out
