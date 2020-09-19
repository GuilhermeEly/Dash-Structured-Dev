import dash
external_scripts = ['https://cdn.plot.ly/plotly-locale-pt-br-latest.js']

app = dash.Dash(__name__,external_scripts=external_scripts, suppress_callback_exceptions=True)
app.scripts.config.serve_locally = False
server = app.server
