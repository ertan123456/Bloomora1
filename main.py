"""
main script
dependencies: dash, plotly, pandas, pyinaturalist
main.py çalıştırılarak başlat
"""
from moduller.calculations import STATE_BBOX as STATE_BBOX, get_counts_parallel as parallel, count_observations_bbox 
from typing import Dict, Tuple, List
import dash
from dash import Dash, html, dcc, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
from moduller import fixes as fixes


# ortaları al
for s, b in STATE_BBOX.items():
    b["clng"] = fixes.mid_lon(b["swlng"], b["nelng"]) 
    b["clat"] = fixes.mid_lon(b["swlat"], b["nelat"])
 

ALL_STATES = sorted(STATE_BBOX.keys()) # keyleri sırala ve liste yap


"""
dash kısım – arayüz ve isim (dash html)
"""
app: Dash = Dash(__name__)
app.title = "Flower Map - Bloomora"
app.layout = html.Div([
    html.Div([
        html.H1("Bloomora Observation Map"),
        html.P("Type a species name, pick a date range, select your preferred states, then fetch counts. Dot size = number of observations."),
    ], style={"maxWidth": "1000px", "margin": "0 auto", "padding": "16px", "backgroundColor": "#f9f9f9"}),

    html.Div([
        html.Div([
            html.Label("taxon (species or genus)"),
            dcc.Input(id="taxon", type="text", value="Taraxacum officinale", debounce=True, style={"width": "100%"}),
        ], style={"flex": 2, "minWidth": 280}),
        html.Div([
            html.Label("Start date (YYYY-MM-DD)"),
            dcc.Input(id="d1", type="text", value="2025-01-01", debounce=True, style={"width": "100%"}),
        ], style={"flex": 1, "minWidth": 180, "marginLeft": 12}),
        html.Div([
            html.Label("End date (YYYY-MM-DD)"),
            dcc.Input(id="d2", type="text", value="2025-10-31", debounce=True, style={"width": "100%"}),
        ], style={"flex": 1, "minWidth": 180, "marginLeft": 12}),
    ], style={"display": "flex", "gap": "12px", "alignItems": "flex-end", "maxWidth": "1000px", "margin": "0 auto", "padding": "0 16px"}),

    html.Div([
        html.Label("States"),
        dcc.Dropdown(id="states", options=[{"label": s, "value": s} for s in ALL_STATES], multi=True, value =["New York", "California", "Texas", "Florida", "Washington",], style={"borderColor": "#28a745"}, placeholder="Select states to query",),
    ], style={"maxWidth": "1000px", "margin": "12px auto", "padding": "0 16px",}),

    html.Div([
        html.Button("Fetch counts", id="go", n_clicks=0, style={"padding": "10px 16px", "backgroundColor": "#28a745"}),
        html.Span(id="status", style={"marginLeft": 12}),
    ], style={"maxWidth": "1000px", "margin": "0 auto", "padding": "0 16px 12px",}),

    dcc.Loading([
        dcc.Graph(id="map", figure=px.scatter_mapbox(pd.DataFrame({"lat":[],"lon":[]}), lat="lat", lon="lon", zoom=3, height=640, mapbox_style="open-street-map"))
    ], type="circle"),

    html.Div([
        html.H3("Counts by state"),
        dash_table.DataTable(id="table", columns=[
            {"name": "State", "id": "state"},
            {"name": "Observations", "id": "count"},
        ], data=[], page_size=10, style_table={"maxWidth": "800px",})
    ], style={"maxWidth": "1000px", "margin": "0 auto", "padding": "0 16px 24px"})
], style={"backgroundColor": "#FFFFFFFF"} )



# callbackleri hookla
@app.callback(
    Output("map", "figure"),
    Output("table", "data"),
    Output("status", "children"),
    Input("go", "n_clicks"),
    State("taxon", "value"),
    State("d1", "value"),
    State("d2", "value"),
    State("states", "value"),
    prevent_initial_call=True,
)


# main fonksiyon (eşzamanlı alma fonsiyonunu kullanır)
def do_fetch(_, tax, d1, d2, states):
    if not states:
        return dash.no_update, dash.no_update, "Select at least one state."
    
    states = list(dict.fromkeys(states))
    df = parallel(tax, d1, d2, states)
    
    """
    eğer boşsa düz return at
    """
    if df.empty:
        fig = px.scatter_mapbox(pd.DataFrame({"lat":[],"lon":[]}), lat="lat", lon="lon", zoom=3, height=640, mapbox_style="open-street-map")
        return fig, [], f"No observations found for '{tax}' between {d1} and {d2}."

    """
    ortalamadan bir merkez belirle
    """
    center_lat = float(df["lat"].mean())
    center_lon = float(df["lon"].mean())

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        size="count",
        size_max=40,
        hover_name="state",
        hover_data={"count": True, "lat": False, "lon": False},
        color="count",
        zoom=3,
        height=680,
        mapbox_style="open-street-map", # sokağa kadar zoom
        title=f"{tax} observations by state ({d1} → {d2})",
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), mapbox=dict(center=dict(lat=center_lat, lon=center_lon)))

    table_data = df[["state", "count"]].to_dict("records")
    status = f"Fetched counts for {len(df)} state(s). Total = {int(df['count'].sum())} observations."
    return fig, table_data, status

# çalıştır
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
