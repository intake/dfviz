from .widget import MainWidget as DFViz
from .example import run_example

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
