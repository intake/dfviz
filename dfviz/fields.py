
plot_requires = {
    'area': ['multi_y'],
    'bar': ['multi_y'],
    'box': ['multi_y'],
    'bivariate': ['x', 'y'],
    'heatmap': ['x', 'y', 'C'],
    'hexbin': ['x', 'y'],
    'hist': ['multi_y'],
    'line': ['multi_y', 'x'],
    'kde': ['multi_y'],
    'scatter': ['y'],
    'table': ['columns'],
    'violin': ['y']
}
plot_allows = {
    'area': ['x', 'stacked', 'logy'],
    'bar': ['x', 'by', 'groupby', 'stacked', 'logy'],
    'box': ['by', 'invert'],
    'bivariate': ['colorbar'],
    'heatmap': ['colorbar'],
    'hexbin': ['colorbar'],
    'hist': ['by', 'bins'],
    'kde': ['by'],
    'line': ['logx', 'logy'],
    'scatter': ['x', 'color', 'marker', 'colorbar', 'cmap', 'size', 'logx',
                'logy'],
    'table': [],
    'violin': ['by', 'groupby']
}
all_names = set(sum(plot_allows.values(), []))
field_names = {'x', 'y', 'C', 'color', 'multi_y', 'by', 'groupby', 'columns',
               'size'}
option_names = [n for n in all_names if n not in field_names] + [
    'color', 'alpha', 'legend', 'size']
