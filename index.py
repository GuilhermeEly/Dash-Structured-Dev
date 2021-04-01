import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from app import server
from apps import layout

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Ir para app FPY DASHBOARD', href='/apps/layout')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/layout':
        return layout.layout
    else:
        return index_page

if __name__ == '__main__':
    #Para rodar em Desenvolvimento
    server.run(host='0.0.0.0', port=8050)

    #Para rodar em LAN
    #app.run_server(debug=False, port=8080, host='0.0.0.0')
