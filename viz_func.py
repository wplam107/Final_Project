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

# Function to create 2D plot of principal components with highlighted areas of clusters
def two_d(mod, viz_df=viz_df, components=['pc1', 'pc3']):
    n_clusters = len(viz_df[mod].unique())
    c_label = list(viz_df[mod].unique())
    color_map = {'0': 'green', '1': 'blue', '2': 'red', '-1': 'fuchsia'}
    fig = px.scatter(viz_df,
                     x=components[0],
                     y=components[1],
                     symbol='source',
                     color=mod,
                     color_discrete_map=color_map,
                     opacity=0.8,
                     hover_name='headline',
                     hover_data=[mod, 'date'],
                    )
    
    fig.update_layout(legend_orientation="v")
    
    # Create cluster areas
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
    
    fig.update_layout(xaxis_title=f"Principal Component: {components[0][2]}",
                      yaxis_title=f"Principal Component: {components[1][2]}",
                      font=dict(family='Arial',
                                size=12,
                                color='#7f7f7f'))
    
    fig.show()

# Function for 3D plot
def three_d(mod, viz_df=viz_df, components=['pc1', 'pc4', 'pc5']):
    fig = px.scatter_3d(viz_df, x=components[0], y=components[1], z=components[2],
                        color=mod, symbol='source', opacity=0.8,
                        hover_name='headline', hover_data=[mod])
    fig.update_layout(showlegend=True)
    fig.show()

# Function to group sources by model cluster
def source_group(mod):
    labels = sorted(viz_df[mod].unique())
    a = pd.DataFrame(viz_df.groupby('source')[mod].value_counts(normalize=True, sort=False))
    a = round(a.unstack() * 100, 2)
    a = np.where(a.isna(), 0, a)
    return labels, a

# Function for horizontal bar chart showing proportions of clusters by source
def h_bar(mod):
    sources = ['ABC (Australia)', 'CCTV', 'CNN', 'Reuters', 'SCMP']
    labels, ls = source_group(mod)
    x_data = ls
    y_data = sources
    top_labels = labels
    colors = ['rgba(38, 24, 74, 0.8)', 'rgba(71, 58, 131, 0.8)',
              'rgba(122, 120, 168, 0.8)', 'rgba(164, 163, 204, 0.85)']

    fig = go.Figure()

    for i in range(0, len(x_data[0])):
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1)
                )
            ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0.15, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
        margin=dict(l=10, r=40, t=140, b=80),
        showlegend=False,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.14, y=yd,
                                xanchor='right',
                                text=str(yd),
                                font=dict(family='Arial', size=10,
                                          color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))
        # labeling the first percentage of each bar (x_axis)
        annotations.append(dict(xref='x', yref='y',
                                x=xd[0] / 2, y=yd,
                                text=str(xd[0]) + '%',
                                font=dict(family='Arial', size=10,
                                          color='rgb(248, 248, 255)'),
                                showarrow=False))
        # labeling the first cluster of a model (on the top)
        if yd == y_data[-1]:
            annotations.append(dict(xref='x', yref='paper',
                                    x=xd[0] / 2, y=1.1,
                                    text=top_labels[0],
                                    font=dict(family='Arial', size=10,
                                              color='rgb(67, 67, 67)'),
                                    showarrow=False))
        space = xd[0]
        for i in range(1, len(xd)):
            # labeling the rest of percentages for each bar (x_axis)
            annotations.append(dict(xref='x', yref='y',
                                    x=space + (xd[i]/2), y=yd,
                                    text=str(xd[i]) + '%',
                                    font=dict(family='Arial', size=10,
                                              color='rgb(248, 248, 255)'),
                                    showarrow=False))
            # Labeling clusters of model
            if yd == y_data[-1]:
                annotations.append(dict(xref='x', yref='paper',
                                        x=space + (xd[i]/2), y=1.1,
                                        text=top_labels[i],
                                        font=dict(family='Arial', size=10,
                                                  color='rgb(67, 67, 67)'),
                                        showarrow=False))
            space += xd[i]

    fig.update_layout(annotations=annotations)
    fig.update_layout(
        title={'text': f'{mod} Cluster Groups by Source',
               'y':0.9,
               'x':0.5,
               'xanchor': 'center',
               'yanchor': 'top'},
               font=dict(
                   family='Arial',
                   size=18,
                   color='#7f7f7f'))
    fig.show()