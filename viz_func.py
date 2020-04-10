import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

def two_d(mod, viz_df=None, n_clusters=2):
    color_map = {'0': 'green', '1': 'blue', '2': 'red'}
    fig = px.scatter(viz_df, x='pc1', y='pc3',
                     color=mod,
                     color_discrete_map=color_map, opacity=0.8)
    fig.update_layout(legend_orientation="h")
    dicts = []
    for i in range(n_clusters):
        a = dict(type="circle", xref="x", yref="y",
                 x0=min(viz_df.loc[viz_df[mod] == f'{i}' ]['pc1']),
                 y0=min(viz_df.loc[viz_df[mod] == f'{i}' ]['pc3']),
                 x1=max(viz_df.loc[viz_df[mod] == f'{i}' ]['pc1']),
                 y1=max(viz_df.loc[viz_df[mod] == f'{i}' ]['pc3']),
                 opacity=0.2, fillcolor=color_map[f'{i}'],
                 line_color=color_map[f'{i}'])
        dicts.append(a)
         
    fig.update_layout(shapes=dicts)
    fig.update_layout(
        title={'text': f'K-Means Clusters (n={n_clusters}) in 2D (n-components=6)',
               'y':0.9,
               'x':0.5,
               'xanchor': 'center',
               'yanchor': 'top'},
        font=dict(family='Arial',
                  size=18,
                  color='#7f7f7f'))
    
    fig.update_layout(xaxis_title="Principal Component 1",
                      yaxis_title="Principal Component 3",
                      font=dict(family='Arial',
                                size=12,
                                color='#7f7f7f'))

    fig.show()