import os
import datetime as dt
import dash
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from PowerDatabase import PowerDatabase


GRAPH_INTERVAL = 1000

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Wind Speed Dashboard"

server = app.server

database = PowerDatabase()

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [
        html.H5(
            "Hello, is it me your looking for", "title"
        ),
        html.Div(
        [
            dcc.Graph(
                id="wind-speed",
                figure=dict(
                    layout=dict(
                        plot_bgcolor=app_color["graph_bg"],
                        paper_bgcolor=app_color["graph_bg"],
                        )
                    ),
            ),
            dcc.Interval(
                id="wind-speed-update",
                interval=int(GRAPH_INTERVAL),
                n_intervals=0,
            )
        ])
    ]
)

def make_current_time_series(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["timestamp"], y=data["current"]))
    fig.update_layout(yaxis_range=(0, 1500))
    return fig

def get_new_data_from_database(last_update):
    pass

@app.callback(
    Output("wind-speed", "figure"), [Input("wind-speed-update", "n_intervals")]
)
def gen_wind_speed(interval):

    data = database.fetch_data(123)
    return make_current_time_series(data)

if __name__ == "__main__":
    app.run_server()