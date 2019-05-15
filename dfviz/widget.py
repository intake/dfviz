import inspect
import panel as pn
from hvplot import hvPlot

plot_requires = {
    'bar': ['multi_y']
}
plot_allows = {
    'bar': ['x', 'stacked']
}


class SigSlot(object):

    def __init__(self):
        self.sigs = {}
        self.map = {}

    def register(self, widget, name, thing='value'):
        self.sigs[name] = {'widget': widget, 'callbacks': [], 'thing': thing}
        wn = "-".join([widget.name, thing])
        self.map[wn] = name
        widget.param.watch(self.signal, thing, onlychanged=True)

    def connect(self, name, callback):
        self.sigs[name]['callbacks'].append(callback)

    def signal(self, event):
        wn = "-".join([event.obj.name, event.name])
        if wn in self.map and self.map[wn] in self.sigs:
            for callback in self.sigs[self.map[wn]]['callbacks']:
                callback(event.new)

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
        self.autoplot = pn.widgets.Checkbox(name='Auto Plot', value=False)
        self.plot = pn.widgets.Button(name='Plot', disabled=True)
        plotcont = pn.Row(self.method, self.autoplot, self.plot)

        self.register(self.autoplot, 'autoplot_toggled')
        self.register(self.plot, 'plot_clicked', 'clicks')

        self.connect('autoplot_toggled',
                     lambda x: setattr(self.plot, 'disabled', not x))
        self.connect('plot_clicked', self.draw)

        self.panel = pn.Column(plotcont, self.control.panel, self.output)

    def draw(self, *args):
        kwargs = self.control.kwargs
        kwargs['kind'] = self.method.value
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
        # self.style = StylePane()
        self.panel = pn.Tabs(self.sample.panel, self.fields.panel,
                             background=(230, 230, 230))

    @property
    def kwargs(self):
        return self.fields.kwargs


def make_option_widget(name, columns, optional=False):
    if name in ['multi_y', 'columns']:
        if name == 'multi_y':
            name = 'y'
        return pn.widgets.MultiSelect(options=columns, name=name)
    if name in ['x', 'y', 'z', 'by']:
        options = ([None] + columns) if optional else columns
        return pn.widgets.Select(options=options, name=name)
    if name in ['stacked']:
        return pn.widgets.Checkbox(name='stacked')


class FieldsPane(SigSlot):

    def __init__(self, columns):
        super().__init__()
        self.columns = columns
        self.panel = pn.Column(name='Fields')
        self.setup()

    def setup(self, method='bar'):
        self.panel.clear()
        for req in plot_requires[method]:
            w = make_option_widget(req, self.columns)
            self.panel.append(w)
        for nreq in plot_allows[method]:
            w = make_option_widget(nreq, self.columns, True)
            self.panel.append(w)

    @property
    def kwargs(self):
        return {p.name: p.value for p in self.panel}


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

        self.register(self.sample, 'sample_toggled')
        self.register(self.how, 'how_chosen')

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
