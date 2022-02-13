import os
import datetime as dt
import dash
from dash import dcc
from dash import html
import pandas as pd

from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output, State
from PowerDatabase import PowerDatabase, FakePowerDatabase


# Parameters
graph_update_int = 10000

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

database = FakePowerDatabase()

app.title = "Power Meter Dashboard"
server = app.server

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}
plotly_colours = px.colors.qualitative.Plotly
num_plotly_colours = len(plotly_colours)
print(plotly_colours)

app.layout = html.Div(
    [
        html.H1(
            "Current Consumption Dashboard",
            style={"text-align": "center"}
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
        ], style={"margin": "20pt", "padding": "16px", "background-color": "white", "border-radius": "5px"}),
        html.Div([
            html.Div([
                html.H4("Show data from", style={"margin-top":"0px"}),
                dcc.Dropdown(options=[{"label": "Past 8 hours", "value": 8},
                                      {"label": "Past day", "value": 24},
                                      {"label": "Past 7 days", "value": 168},
                                      {"label": "All time", "value": 999999999}],
                             value = 8,
                             id="data-time-dropdown", style={"font-family":"sans-serif"}),
            ], style = {"flex-grow": "1", "background-color": "white", "border-radius": "5px", "padding": "16px"}),
            html.Div([
                html.Div(id="machine-names", style={"margin-top": "18px", "flex-grow":"1"}),
                html.Div([
                    html.H4("Mean Current Draw", style={"margin-top":"0px", "flex-grow":"2"}),
                    html.Div(id="mean-current-draw")
                ], style={"flex-grow":"2"}),
                html.Div([
                    html.H4("Maximum Current Draw", style={"margin-top":"0px"}),
                    html.Div(id="max-current-draw")
                ], style={"flex-grow":"2"})],
                style= {"display": "flex", "flex-direction": "row", "flex-grow": "3",
                        "background-color": "white", "border-radius": "5px", "padding": "16px", "margin-left":"20px"})
            ], style={"margin": "20pt", "display": "flex", "flex-direction": "row"})
    ],
)

def make_current_time_series(data, machine_ids):
    fig = go.Figure()
    for machine in machine_ids:
        fig.add_trace(go.Scatter(x=data[data["uid"] == machine]["timestamp"]
                                 , y=data[data["uid"] == machine]["current"], name=machine))

    fig.update_layout(yaxis_range=(0, data["current"].max() * 1.1))
    fig.update_layout(yaxis_title="Current (mA)", xaxis_title="Time")
    # fig.update_layout(paper_bgcolor='slategray')
    fig.layout.showlegend=True
    return fig

def get_average_and_max_powers(data):
    means = data.groupby("uid")["current"].mean()
    maxes = data.groupby("uid")["current"].max()

    means = means.round(1)
    maxes = maxes.round(1)

    mean_elements = [html.H1("{} mA".format( mean), style={"align-text":"center",
                                                           "color": plotly_colours[i%num_plotly_colours]})
                     for i, (_, mean) in enumerate(means.items())]
    max_elements = [html.H1("{} mA".format(max), style={"align-text":"center",
                                                        "color": plotly_colours[i%num_plotly_colours]})
                     for i, (_, max) in enumerate(maxes.items())]

    return mean_elements, max_elements

def get_machine_name_headers(machine_ids):
    return [html.H4(name, style={"align-text":"center", "padding":"10px",
                                    "color": plotly_colours[i%num_plotly_colours]})
            for i, name in enumerate(machine_ids)]

@app.callback(
    Output("power-time-series", "figure"),
    Output("mean-current-draw", "children"),
    Output("max-current-draw", "children"),
    Output("machine-names", "children"),
    Input("power-data-update", "n_intervals"),
    Input("data-time-dropdown", "value")
)
def update_power_data(interval, past_data):
    past_data = timedelta(hours=past_data)
    earliest_data = datetime.now() - past_data
    data = database.fetch_data(earliest_data)
    machine_ids = database.get_machine_ids()

    current_time_fig = make_current_time_series(data, machine_ids)
    mean_elements, max_elements = get_average_and_max_powers(data)

    machine_names = get_machine_name_headers(machine_ids)

    return current_time_fig, \
           mean_elements, max_elements, machine_names

if __name__ == "__main__":
    app.run_server()