
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: YOUR GITHUB USER NAME                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: YOUR REPOSITORY URL                                                                     -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import plotly.graph_objects as pl

def grafica(x, y, titulo, xtitulo, ytitulo):
    graf = pl.Figure()
    graf.add_trace(pl.Scatter(x=x, y=y, mode='lines', name=ytitulo, line=dict(color='green'), hovertemplate='<extra></extra>'+'Capital: $%{y:2,.2f}'+'<br>Date: %{x}<br>'))
    graf.update_layout(title=titulo, xaxis_title=xtitulo, yaxis_title=ytitulo)
    graf.update_xaxes(showspikes=True)
    graf.update_yaxes(showspikes=True)
    return graf
