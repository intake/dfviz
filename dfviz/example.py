"""
Executable example of the interface with random data.

Call as:
$ python example.py  # in this directory
or
$ python -c "import dfviz; dfviz.run_example()"
from anywhere, if dfviz has been installed.
"""

import numpy as np
import pandas as pd
from dfviz import DFViz


def run_example(show=True):
    """Display example dataset in the interface

    Parameters
    ----------
    show : bool
        If True, automatically opens new browser tab with the interface.

    Returns
    -------
    A dfviz.DFViz instance. To display, you can use widget.show() or
    allow widget.panel to be rendered in a notebook.
    """
    try:
        import dask.dataframe as dd
    except ImportError:
        dd = False
    N = 1000
    df = pd.DataFrame({
        'a': range(N),
        'b': np.random.rand(N),
        'c': np.random.randn(N),
        'd': np.random.choice(['A', 'B', 'C'], size=N)
    })
    if dd:
        df = dd.from_pandas(df, 2)
    kwargs = {
        'alpha': 0.7,
        'color': 'a',
        'marker': 's',
        'colorbar': True,
        'cmap': 'Viridis',
        'size': 55,
        'width': 600,
        'height': 600,
        'xlim': (0, 1000.0),
        'ylim': (-2, 2),
        'y': 'c',
        'x': 'a',
        'kind': 'scatter',
        'Sample': False
    }
    wid = DFViz(df, **kwargs)
    if show:
        try:
            wid.show()
        except KeyboardInterrupt:
            pass
    return wid


if __name__ == '__main__':
    wid = run_example()
