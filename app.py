import dash
from config.serverConfig import BaseConfig
from flask import Flask

server = Flask(__name__)
server.config.from_object(BaseConfig)

app = dash.Dash(__name__,
                 server=server,
                 url_base_pathname='/'
                 )


#app = dash.Dash(__name__, suppress_callback_exceptions=True)

#server = app.server
