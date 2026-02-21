"""Sources Ranked by Emissions — Scattergeo map page."""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd

from services.api import get_sources, get_gases, SECTORS

dash.register_page(
    __name__,
    path="/sources-ranked",
    name="Sources Ranked",
    title="Sources Ranked by Emissions — Emissions Sources",
)

# Pre-fetch gas options
_gases = get_gases()
_priority_gases = ["co2e_100yr", "co2e_20yr", "co2", "ch4", "n2o"]
_gas_options = [{"label": g, "value": g} for g in _priority_gases if g in _gases] + [
    {"label": g, "value": g} for g in _gases if g not in _priority_gases
]

_sector_options = [{"label": s.replace("-", " ").title(), "value": s} for s in SECTORS]

_year_options = [{"label": str(y), "value": y} for y in range(2024, 2020, -1)]

_limit_options = [
    {"label": "50", "value": 50},
    {"label": "100", "value": 100},
    {"label": "200", "value": 200},
    {"label": "500", "value": 500},
]


layout = html.Div(
    [
        # Back link
        dcc.Link("← Back", href="/", className="back-link"),
        # Title
        html.H1("Sources Ranked By Emissions", className="page-title"),
        # Filters
        html.Div(
            [
                html.Span("Filters", className="filters-label"),
                html.Div(
                    [
                        html.Label("Year", className="filter-label"),
                        dcc.Dropdown(
                            id="src-year",
                            options=_year_options,
                            value=2024,
                            clearable=False,
                            className="filter-dropdown",
                        ),
                    ],
                    className="filter-group",
                ),
                html.Div(
                    [
                        html.Label("Gas", className="filter-label"),
                        dcc.Dropdown(
                            id="src-gas",
                            options=_gas_options,
                            value="co2e_100yr",
                            clearable=False,
                            className="filter-dropdown filter-dropdown-wide",
                        ),
                    ],
                    className="filter-group",
                ),
                html.Div(
                    [
                        html.Label("Sectors", className="filter-label"),
                        dcc.Dropdown(
                            id="src-sectors",
                            options=_sector_options,
                            value=[],
                            multi=True,
                            placeholder="All",
                            className="filter-dropdown filter-dropdown-wide",
                        ),
                    ],
                    className="filter-group",
                ),
                html.Div(
                    [
                        html.Label("Limit", className="filter-label"),
                        dcc.Dropdown(
                            id="src-limit",
                            options=_limit_options,
                            value=500,
                            clearable=False,
                            className="filter-dropdown",
                        ),
                    ],
                    className="filter-group",
                ),
            ],
            className="filters-row",
        ),
        # Loading + Map
        dcc.Loading(
            html.Div(
                [
                    dcc.Graph(
                        id="sources-map",
                        config={"displayModeBar": True, "scrollZoom": True},
                    ),
                ],
                className="map-container",
            ),
            type="circle",
            color="#0d9488",
        ),
    ],
    className="data-page",
)


@callback(
    Output("sources-map", "figure"),
    [
        Input("src-year", "value"),
        Input("src-gas", "value"),
        Input("src-sectors", "value"),
        Input("src-limit", "value"),
    ],
)
def update_map(year, gas, sectors, limit):
    """Fetch ranked sources and plot on a Scattermap."""
    sector_param = sectors if sectors else None
    sources = get_sources(year=year, gas=gas, sectors=sector_param, limit=limit)

    fig = go.Figure()

    if sources:
        df = pd.DataFrame(sources)
        df["lat"] = df["centroid"].apply(lambda c: c["latitude"])
        df["lon"] = df["centroid"].apply(lambda c: c["longitude"])

        # Format emissions for display
        df["emissions_fmt"] = df["emissionsQuantity"].apply(
            lambda x: f"{x:,.0f}" if x < 1e6 else f"{x / 1e6:,.1f}M"
        )

        fig.add_trace(
            go.Scattermap(
                lat=df["lat"],
                lon=df["lon"],
                marker=dict(
                    size=df["emissionsQuantity"].apply(
                        lambda x: max(8, min(35, (x / df["emissionsQuantity"].max()) * 35))
                    ),
                    color=df["emissionsQuantity"],
                    colorscale="RdYlBu_r",
                    colorbar=dict(
                        title="Emissions Quantity",
                        titleside="right",
                        thickness=15,
                        len=0.6,
                    ),
                    opacity=0.75,
                ),
                text=df.apply(
                    lambda row: (
                        f"{row['name']}\n"
                        f"Sector: {row['sector'].replace('-', ' ').title()}\n"
                        f"Country: {row['country']}\n"
                        f"Emissions: {row['emissions_fmt']} tonnes"
                    ),
                    axis=1,
                ),
                hoverinfo="text",
            )
        )

    fig.update_layout(
        map=dict(
            style="open-street-map",
            center=dict(lat=20, lon=0),
            zoom=1.3,
        ),
        margin=dict(l=0, r=0, t=10, b=10),
        height=550,
    )

    return fig
