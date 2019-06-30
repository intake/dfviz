import dask.dataframe as dd
import numpy as np
import pandas as pd
from dfviz.widget import MainWidget


def run_example():
    N = 1000
    df = pd.DataFrame({
        'a': range(N),
        'b': np.random.rand(N),
        'c': np.random.randn(N),
        'd': np.random.choice(['A', 'B', 'C'], size=N)
    })
    # widget = MainWidget(df)
    wid = MainWidget(dd.from_pandas(df, 2))
    try:
        wid.show()
    finally:
        return wid


if __name__ == '__main__':
    wid = run_example()
