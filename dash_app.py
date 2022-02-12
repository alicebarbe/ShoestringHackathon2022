import os
import datetime as dt
import dash
from dash import dcc
from dash import html
import pandas as pd

from datetime import datetime, timedelta
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from PowerDatabase import PowerDatabase


# Parameters
graph_update_int = 10000
past_data = timedelta(hours=8)
machine_ids = ["robot1"]


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

database = PowerDatabase()

app.title = "Power Meter Dashboard"
server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [
        html.H5(
            "Hello, is it me your looking for", "title"
        ),
        html.Div(
        [
            dcc.Graph(
                id="power-time-series",
                figure=dict(
                    layout=dict(
                        plot_bgcolor=app_color["graph_bg"],
                        paper_bgcolor=app_color["graph_bg"],
                        )
                    ),
            ),
            dcc.Interval(
                id="power-data-update",
                interval=int(graph_update_int),
                n_intervals=0,
            )
        ])
    ]
)

def make_current_time_series(data):
    fig = go.Figure()
    for machine in machine_ids:
        fig.add_trace(go.Scatter(x=data[data["uid"] == machine]["timestamp"]
                                 , y=data[data["uid"] == machine]["current"], name=machine))

    fig.update_layout(yaxis_range=(0, data["current"].max() * 1.1))
    return fig

@app.callback(
    Output("power-time-series", "figure"), Input("power-data-update", "n_intervals")
)
def update_power_data(interval):
    earliest_data = datetime.now() - past_data
    data = database.fetch_data(earliest_data)
    return make_current_time_series(data)

if __name__ == "__main__":
    app.run_server()