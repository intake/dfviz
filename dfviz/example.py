"""
Executable example of the interface with random data.

Call as:
$ python example.py  # in this directory
or
$ python -c "import dfviz; dfviz.run_example()"
from anywhere, if dfviz has been installed.
"""

import dask.dataframe as dd
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
    N = 1000
    df = pd.DataFrame({
        'a': range(N),
        'b': np.random.rand(N),
        'c': np.random.randn(N),
        'd': np.random.choice(['A', 'B', 'C'], size=N)
    })
    # widget = MainWidget(df)
    wid = DFViz(dd.from_pandas(df, 2))
    if show:
        try:
            wid.show()
        except KeyboardInterrupt:
            pass
    return wid


if __name__ == '__main__':
    wid = run_example()
