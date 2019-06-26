import logging
logger = logging.getLogger('dfviz')
logger.setLevel('DEBUG')


def pretty_describe(object, nestedness=0, indent=2):
    """Maintain dict ordering - but make string version prettier"""
    if not isinstance(object, dict):
        return str(object)
    sep = f'\n{" " * nestedness * indent}'
    out = sep.join((f'{k}: {pretty_describe(v, nestedness + 1)}'
                    for k, v in object.items()))
    if nestedness > 0 and out:
        return f'{sep}{out}'
    return out
