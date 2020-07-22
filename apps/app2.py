from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
from app import app


X = deque(maxlen=20)
X.append(1)
Y = deque(maxlen=20)
Y.append(1)



layout = html.Div(
    [
        html.H3('App 2'),
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1500
        ),
        dcc.Link('Go to App 1', href='/apps/app1')
    ]
)

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])

def update_graph_scatter(n):
    X.append(X[-1]+1)
    Y.append(Y[-1]+Y[-1]*random.uniform(-0.1,0.1))

    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X)-1,max(X)+1]),
                                                yaxis=dict(range=[min(Y)-0.1,max(Y)+0.1]),)}

