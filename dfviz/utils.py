import logging
logger = logging.getLogger('dfviz')
logger.setLevel('DEBUG')


def pretty_describe(object, nestedness=0, indent=2):
    """Nice YAML-like text version of given dict/object

    Maintains dict ordering
    """
    if not isinstance(object, dict):
        return str(object)
    sep = f'\n{" " * nestedness * indent}'
    out = sep.join((f'{k}: {pretty_describe(v, nestedness + 1)}'
                    for k, v in object.items()))
    if nestedness > 0 and out:
        return f'{sep}{out}'
    return out
