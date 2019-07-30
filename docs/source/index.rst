DFVIZ: interactive plotting of dataframes
=========================================

``dfviz`` is a small package for interactive visualisation of `Pandas`_
or `Dask`_ dataframes. It is built upon `Panel`_ and `hvPlot`_ and can be used
either within a notebook environment, as a stand-alone application, or as one of the
visualisation modules within the `Intake`_ GUI.

.. _Dask: https://docs.dask.org/en/latest/dataframe.html
.. _hvPlot: https://hvplot.pyviz.org
.. _Intake: https://intake.readthedocs.io
.. _Pandas: https://pandas.pydata.org
.. _Panel: https://panel.pyviz.org

Installation
------------

With a conda environment, you can use

.. code-block::

    $ conda install -c conda-forge dfviz


or, in general you can install the released version

.. code-block::

    $ pip install dfviz

or development version

.. code-block::

    $ pip install git+https://github.com/intake/dfviz


For both ``pip``-based methods, it is generally better to install the requirements
manually beforehand.

Example
-------

To run the interface with some random data, you can execute

.. code-block::

    python -c "import dfviz; dfviz.example.run_example()"

which will open a new tab in a browser, ready for a plot to be defined.
Just press Plot to get a colourful scatter-plot output.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
