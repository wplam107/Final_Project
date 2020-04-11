import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import plotly.express as px
import plotly.graph_objects as go

file = open('viz_df.p', 'rb')
viz_df = pickle.load(file)
file.close()

def two_d(mod, viz_df=viz_df, components=['pc1', 'pc3']):
    n_clusters = len(viz_df[mod].unique())
    c_label = list(viz_df[mod].unique())
    color_map = {'0': 'green', '1': 'blue', '2': 'red', '-1': 'fuchsia'}
    fig = px.scatter(viz_df, x=components[0], y=components[1], symbol='source',
                     color=mod, color_discrete_map=color_map, opacity=0.8)
    fig.update_layout(legend_orientation="h")
    dicts = []
    for i in c_label:
        if i != '-1':
            a = dict(type="circle", xref="x", yref="y",
                     x0=min(viz_df.loc[viz_df[mod] == f'{i}' ][components[0]]),
                     y0=min(viz_df.loc[viz_df[mod] == f'{i}' ][components[1]]),
                     x1=max(viz_df.loc[viz_df[mod] == f'{i}' ][components[0]]),
                     y1=max(viz_df.loc[viz_df[mod] == f'{i}' ][components[1]]),
                     opacity=0.2, fillcolor=color_map[f'{i}'],
                     line_color=color_map[f'{i}'])
            dicts.append(a)   
    fig.update_layout(shapes=dicts)
    fig.update_layout(
        title={'text': f'{mod} (n={n_clusters}) in 2D (n-components=6)',
               'y':0.9,
               'x':0.5,
               'xanchor': 'center',
               'yanchor': 'top'},
        font=dict(family='Arial',
                  size=18,
                  color='#7f7f7f'))
    fig.update_layout(xaxis_title=f"Principal Component: {components[0]}",
                      yaxis_title=f"Principal Component: {components[1]}",
                      font=dict(family='Arial',
                                size=12,
                                color='#7f7f7f'))
    fig.show()