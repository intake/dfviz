import inspect
import panel as pn
from hvplot import hvPlot
from hvplot.converter import HoloViewsConverter as HVC


plot_types = list(_ for _ in dir(hvPlot) if not _.startswith('_'))
plots_needs = {
    k: set(inspect.signature(getattr(hvPlot, k)).parameters) - {'self', 'kwds'}
    for k in plot_types
}

fields = ['x', 'y', 'z', 'text', 'bands', 'by', 'C']
others = {'colorbar': bool, 'stacked': bool, 'where': ['pre', 'mid', 'post'],
          'columns': 'columns'}


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
        wn = "-".join([event.obj.name, event.what])
        for callback in self.sigs[self.map[wn]]['callbacks']:
            callback(event.new)

    def show(self):
        self.panel.show()


class MainWidget(SigSlot):

    def __init__(self, data):
        super().__init__()
        self.data = data
        self.dflike = hasattr(data, 'columns')
        if not self.dflike and not hasattr(data, 'dtype'):
            raise ValueError('Wanted dataframe or array')
        if not self.dflike:
            raise NotImplementedError  # coming soon...
        self.dasky = hasattr(data, 'dask')
        self.control = ControlWidget(self.dflike, self.dasky)
        self.output = pn.Spacer()
        self.panel = pn.Column(self.control, self.output)


class ControlWidget(SigSlot):

    def __init__(self, npartitions, dflike):
        super().__init__()
        self.autoplot = False
        self.sample = SamplePane(npartitions, dflike)

        self.sample.connect('autoplot_toggled',
                            lambda x: print(x))
        # self.fields = FieldPane()
        # self.options = OptionsPane()
        # self.style = StylePane()
        self.panel = pn.Tabs(self.sample.panel)


class SamplePane(SigSlot):

    def __init__(self, npartitions, dflike=True):
        super().__init__()
        self.npartitions = npartitions
        self.autoplot = pn.widgets.Checkbox(name='Auto Plot', value=False)
        self.plot = pn.widgets.Button(name='Plot', disabled=True)
        plotcont = pn.Row(self.autoplot, self.plot)

        self.sample = pn.widgets.Checkbox(name='Sample', value=True)
        op = ['Random', 'Head', 'Tail']
        if npartitions > 1:
            op.append('Partition')
        self.how = pn.widgets.Select(options=op, name='How')
        self.par = pn.widgets.Select()
        self.make_sample_pars('Random')
        sampler = pn.Row(self.sample, self.how, self.par)

        if dflike:
            kinds = sorted(k for k in HVC._kind_mapping if k not in
                           HVC._gridded_types)
        else:
            kinds = list(HVC._gridded_types)
        self.method = pn.widgets.Select(name='Plot Type', options=kinds)
        metho = pn.Row(self.method)

        self.register(self.autoplot, 'autoplot_toggled')
        self.register(self.plot, 'plot_clicked', 'clicks')
        self.register(self.sample, 'sample_toggled')
        self.register(self.how, 'how_chosen')

        self.connect('autoplot_toggled',
                     lambda x: setattr(self.plot, 'disabled', not x))
        self.connect('sample_toggled',
                     lambda x: setattr(self.how, 'disabled', not x) or
                     setattr(self.par, 'disabled', not x))
        self.connect('how_chosen', self.make_sample_pars)

        self.panel = pn.Column(plotcont, sampler, metho, name='Control')

    def make_sample_pars(self, manner):
        opts = {'Random': ('percent', [10, 1, 0.1]),
                'Partition': ('#', list(range(self.npartitions))),
                'Head': ('rows', [10, 100, 1000, 10000]),
                'Tail': ('rows', [10, 100, 1000, 10000])}[manner]
        self.par.name = opts[0]
        self.par.options = opts[1]

    def get_method(self):
        return self.method.value


class FieldSelectors(object):

    def __init__(self, df):

        self.df = df
        self.fields = list(df.columns)
        self.plot_type = pn.widgets.Select(
            name='Plot Type', options=plot_types)
        self.fieldset = pn.layout.Column(background=(200, 200, 200))
        self.opts = pn.layout.Column()
        self.widget = pn.layout.Column(
            self.plot_type, self.fieldset, self.opts,
            background=(230, 230, 230)
        )
        self.outer = pn.layout.Row(self.widget, pn.layout.Row())
        self.refresh()
        self.plot_type.param.watch(self.refresh, 'value', onlychanged=True)

    def refresh(self, *args):
        args = self.args   # current values
        needs = plots_needs[self.plot_type.value]

        self.fieldset.clear()
        for field in fields:
            if field in needs:
                if len(self.fieldset) == 0:
                    self.fieldset.append(
                        pn.widgets.StaticText(value='Fields'))

                s = pn.widgets.Select(options=self.fields, name=field,
                                         value=args.get(field, None))
                self.fieldset.append(s)
                s.param.watch(self.draw, 'value', onlychanged=True)

        self.opts.clear()
        for field in others:
            if field in needs:
                if len(self.opts) == 0:
                    self.opts.append(pn.widgets.StaticText(value='Options'))

                if others.get(field, None) is bool:
                    s = pn.widgets.Checkbox(name=field)
                elif isinstance(others.get(field, None), list):
                    s = pn.widgets.Select(name=field, options=others[field])
                elif field == 'columns':
                    s = pn.widgets.MultiSelect(name=field, value=self.fields,
                                                  options=self.fields)
                if field in args:
                    s.value = args[field]
                self.opts.append(s)
                s.param.watch(self.draw, 'value', onlychanged=True)

        self.draw()

    @property
    def args(self):
        args = {'kind': self.plot_type.value}
        for s in self.fieldset[1:]:
            args[s.name] = s.value
        for s in self.opts[1:]:
            args[s.name] = s.value
        return args

    def draw(self, *args):
        # TODO: presumably only some changes need a complete redraw
        plot = hvPlot(self.df, **self.args)
        self.outer[1] = pn.pane.HoloViews(plot)


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({
        'a': range(100),
        'b': np.random.rand(100),
        'c': np.random.randn(100),
        'd': np.random.choice(['A', 'B', 'C'], size=100)
    })
    widget = FieldSelectors(df)
    widget.outer.show()
