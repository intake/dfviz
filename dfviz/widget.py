import inspect
import panel as pn
from hvplot import hvPlot
from hvplot.converter import HoloViewsConverter


plot_types = list(_ for _ in dir(hvPlot) if not _.startswith('_'))
plots_needs = {
    k: set(inspect.signature(getattr(hvPlot, k)).parameters) - {'self', 'kwds'}
    for k in plot_types
}

fields = ['x', 'y', 'z', 'text', 'bands', 'by', 'C']
others = {'colorbar': bool, 'stacked': bool, 'where': ['pre', 'mid', 'post'],
          'columns': 'columns'}


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
