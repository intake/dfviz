from bokeh import palettes
import panel as pn
from hvplot import hvPlot

plot_requires = {
    'bar': ['multi_y'],
    'hist': ['multi_y'],
    'area': ['multi_y'],
    'scatter': ['y']
}
plot_allows = {
    'bar': ['x', 'by', 'groupby', 'stacked'],
    'hist': ['by'],
    'area': ['x', 'stacked'],
    'scatter': ['x', 'color', 'marker', 'colorbar', 'cmap', 'size']
}
field_names = ['x', 'y', 'color', 'multi_y', 'by', 'groupby', 'columns']


class SigSlot(object):
    """Signal-slot mixin, for Panel event passing"""

    def __init__(self):
        self._sigs = {}
        self._map = {}

    def _register(self, widget, name, thing='value'):
        """Watch the given attribute of a widget and assign it a named event

        This is normally called at the time a widget is instantiated, in the
        class which owns it.

        Parameters
        ----------
        widget : pn.layout.Panel
            Widget to watch
        name : str
            Name of this event
        thing : str
            Attribute of the given widget to watch
        """
        self._sigs[name] = {'widget': widget, 'callbacks': [], 'thing': thing}
        wn = "-".join([widget.name, thing])
        self._map[wn] = name
        widget.param.watch(self._signal, thing, onlychanged=True)

    @property
    def signals(self):
        """Known named signals of this class"""
        return list(self._sigs)

    def connect(self, name, callback):
        """Associate call back with given event

        The callback must be a function which takes the "new" value of the
        watched attribute as the only parameter. If the callback return False,
        this cancels any further processing of the given event.
        """
        self._sigs[name]['callbacks'].append(callback)

    def _signal(self, event):
        wn = "-".join([event.obj.name, event.name])
        print(wn, event)
        if wn in self._map and self._map[wn] in self._sigs:
            for callback in self._sigs[self._map[wn]]['callbacks']:
                if callback(event.new) is False:
                    break

    def show(self):
        self.panel.show()


class MainWidget(SigSlot):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.dasky = hasattr(data, 'dask')
        self.control = ControlWidget(self.data)
        self.output = pn.Row(pn.Spacer())

        self.method = pn.widgets.Select(
            name='Plot Type', options=list(plot_requires))
        self.autoplot = pn.widgets.Checkbox(name='Auto Plot', value=True)
        self.plot = pn.widgets.Button(name='Plot', disabled=True)
        plotcont = pn.Row(self.method, self.autoplot, self.plot,
                          pn.layout.HSpacer())

        self._register(self.autoplot, 'autoplot_toggled')
        self._register(self.plot, 'plot_clicked', 'clicks')
        self._register(self.method, 'method_changed')

        self.connect('autoplot_toggled',
                     lambda x: setattr(self.plot, 'disabled', x))
        self.connect('plot_clicked', self.draw)
        self.connect('method_changed', self.control.set_method)

        self.panel = pn.Column(plotcont, self.control.panel, self.output)

    def draw(self, *args):
        kwargs = self.control.kwargs
        kwargs['kind'] = self.method.value
        print(kwargs)
        self._plot = hvPlot(self.data)(**kwargs)
        self.output[0] = pn.pane.HoloViews(self._plot)


class ControlWidget(SigSlot):

    def __init__(self, df):
        super().__init__()
        npartitions = getattr(df, 'npartitions', 1)
        self.autoplot = False

        self.sample = SamplePane(npartitions)
        self.fields = FieldsPane(columns=list(df.columns))
        # self.options = OptionsPane()
        self.style = StylePane()
        self.panel = pn.Tabs(self.sample.panel, self.fields.panel,
                             self.style.panel,
                             background=(230, 230, 230))

    def set_method(self, method):
        self.fields.setup(method)
        self.style.setup(method)

    @property
    def kwargs(self):
        kwargs = self.fields.kwargs
        kwargs.update(self.style.kwargs)
        return kwargs


def make_option_widget(name, columns=[], optional=False):
    if name in ['multi_y', 'columns']:
        if name == 'multi_y':
            name = 'y'
        return pn.widgets.MultiSelect(options=columns, name=name)
    if name in ['x', 'y', 'z', 'by', 'groupby', 'color']:
        options = ([None] + columns) if optional else columns
        return pn.widgets.Select(options=options, name=name)
    if name in ['stacked', 'colorbar']:
        return pn.widgets.Checkbox(name=name)
    if name == 'legend':
        return pn.widgets.Select(
            name='legend', value='right',
            options=[None, 'top', 'bottom', 'left', 'right']
        )
    if name == 'alpha':
        return pn.widgets.FloatSlider(name='alpha', start=0, end=1, value=0.9,
                                      step=0.05)
    if name == 'size':
        return pn.widgets.IntSlider(name='size', start=3, end=65, value=12,
                                    step=2)
    if name == 'cmap':
        return pn.widgets.Select(name='cmap', value='Viridis',
                                 options=list(palettes.all_palettes))
    if name == 'marker':
        return pn.widgets.Select(name='marker', value='o',
                                 options=list('s.ov^<>*+x'))


class StylePane(SigSlot):

    def __init__(self):
        self.panel = pn.Column(pn.Spacer(), name='Style')

    def setup(self, method):
        allowed = ['alpha', 'legend'] + plot_allows[method]
        ws = [make_option_widget(nreq) for nreq in allowed
              if nreq not in field_names]
        self.panel[0] = pn.Column(*ws, name='Style')

    @property
    def kwargs(self):
        return {p.name: p.value for p in self.panel[0]}


class FieldsPane(SigSlot):

    def __init__(self, columns):
        super().__init__()
        self.columns = columns
        self.panel = pn.Column(name='Fields')
        self.setup()

    def setup(self, method='bar'):
        self.panel.clear()
        for req in plot_requires[method]:
            if req in field_names:
                w = make_option_widget(req, self.columns)
                self.panel.append(w)
        for nreq in plot_allows[method]:
            if nreq in field_names:
                w = make_option_widget(nreq, self.columns, True)
                self.panel.append(w)

    @property
    def kwargs(self):
        out = {p.name: p.value for p in self.panel}
        y = out.get('y', [])
        if isinstance(y, list) and len(y) == 1:
            out['y'] = y[0]
        return out


class SamplePane(SigSlot):

    def __init__(self, npartitions):
        super().__init__()
        self.npartitions = npartitions

        self.sample = pn.widgets.Checkbox(name='Sample', value=True)
        op = ['Random', 'Head', 'Tail']
        if npartitions > 1:
            op.append('Partition')
        self.how = pn.widgets.Select(options=op, name='How')
        self.par = pn.widgets.Select()
        self.make_sample_pars('Random')

        self._register(self.sample, 'sample_toggled')
        self._register(self.how, 'how_chosen')

        self.connect('sample_toggled',
                     lambda x: setattr(self.how, 'disabled', not x) or
                     setattr(self.par, 'disabled', not x))
        self.connect('how_chosen', self.make_sample_pars)

        # set default value
        self.sample.value = npartitions > 1

        self.panel = pn.Row(self.sample, self.how, self.par, name='Control')

    def make_sample_pars(self, manner):
        opts = {'Random': ('percent', [10, 1, 0.1]),
                'Partition': ('#', list(range(self.npartitions))),
                'Head': ('rows', [10, 100, 1000, 10000]),
                'Tail': ('rows', [10, 100, 1000, 10000])}[manner]
        self.par.name = opts[0]
        self.par.options = opts[1]


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({
        'a': range(100),
        'b': np.random.rand(100),
        'c': np.random.randn(100),
        'd': np.random.choice(['A', 'B', 'C'], size=100)
    })
    widget = ControlWidget(df)
    widget.show()
