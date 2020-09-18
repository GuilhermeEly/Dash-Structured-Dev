import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, app3, app4, app5, app6, dashboard_FPY, dashboard_FPY_Plots, FPY_DASHBOARD


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Ir para app 1', href='/apps/app1'),
    html.Br(),
    dcc.Link('Ir para app 2', href='/apps/app2'),
    html.Br(),
    dcc.Link('Ir para app 3', href='/apps/app3'),
    html.Br(),
    dcc.Link('Ir para app 4', href='/apps/app4'),
    html.Br(),
    dcc.Link('Ir para app 5', href='/apps/app5'),
    html.Br(),
    dcc.Link('Ir para app 6', href='/apps/app6'),
    html.Br(),
    dcc.Link('Ir para app Dashboard FPY', href='/apps/dashboard_FPY'),
    html.Br(),
    dcc.Link('Ir para app Dashboard FPY Plots', href='/apps/dashboard_FPY_Plots'),
    html.Br(),
    dcc.Link('Ir para app FPY DASHBOARD', href='/apps/FPY_DASHBOARD'),
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    elif pathname == '/apps/app3':
        return app3.layout
    elif pathname == '/apps/app4':
        return app4.layout
    elif pathname == '/apps/app5':
        return app5.layout
    elif pathname == '/apps/app6':
        return app6.layout
    elif pathname == '/apps/dashboard_FPY':
        return dashboard_FPY.layout
    elif pathname == '/apps/dashboard_FPY_Plots':
        return dashboard_FPY_Plots.layout
    elif pathname == '/apps/FPY_DASHBOARD':
        return FPY_DASHBOARD.layout
    else:
        return index_page

if __name__ == '__main__':
    #Para rodar em Desenvolvimento
    #app.run_server(debug=True)

    #Para rodar em LAN
    app.run_server(debug=False, port=8080, host='0.0.0.0')
