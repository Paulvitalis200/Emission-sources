"""Aggregate Emissions page — Monthly emissions with filters and charts."""

import dash
from dash import html, dcc, callback, Input, Output
import plotly.graph_objects as go

from services.api import get_emissions, get_gases, get_continents, SECTORS

dash.register_page(
    __name__,
    path="/aggregate-emissions",
    name="Aggregate Emissions",
    title="Aggregate Emissions — Emissions Sources",
)

# Pre-fetch filter options at import time
_gases = get_gases()
_continents = get_continents()

# Common gas options (show most useful ones first)
_priority_gases = ["co2e_100yr", "co2e_20yr", "co2", "ch4", "n2o"]
_gas_options = [{"label": g, "value": g} for g in _priority_gases if g in _gases] + [
    {"label": g, "value": g} for g in _gases if g not in _priority_gases
]

_continent_options = [{"label": "All", "value": "all"}] + [
    {"label": c, "value": c} for c in sorted(_continents)
]

_sector_options = [{"label": s.replace("-", " ").title(), "value": s} for s in SECTORS]

_year_options = [{"label": str(y), "value": y} for y in range(2024, 2014, -1)]


layout = html.Div(
    [
        # Back link
        dcc.Link("← Back", href="/", className="back-link"),
        # Title
        html.H1("Aggregate Emissions", className="page-title"),
        # Filters
        html.Div(
            [
                html.Span("Filters", className="filters-label"),
                html.Div(
                    [
                        html.Label("Year", className="filter-label"),
                        dcc.Dropdown(
                            id="agg-year",
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
                        html.Label("Continent", className="filter-label"),
                        dcc.Dropdown(
                            id="agg-continent",
                            options=_continent_options,
                            value="all",
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
                            id="agg-gas",
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
                            id="agg-sectors",
                            options=_sector_options,
                            value=[],
                            multi=True,
                            placeholder="All",
                            className="filter-dropdown filter-dropdown-wide",
                        ),
                    ],
                    className="filter-group",
                ),
            ],
            className="filters-row",
        ),
        # Loading indicator
        dcc.Loading(
            [
                # Charts row
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(id="agg-total-title", className="chart-title"),
                                dcc.Graph(id="agg-total-chart", config={"displayModeBar": True}),
                            ],
                            className="chart-container",
                        ),
                        html.Div(
                            [
                                html.H3(
                                    id="agg-sector-title",
                                    className="chart-title",
                                ),
                                dcc.Graph(id="agg-sector-chart", config={"displayModeBar": True}),
                            ],
                            className="chart-container",
                        ),
                    ],
                    className="charts-row",
                ),
            ],
            type="circle",
            color="#0d9488",
        ),
    ],
    className="data-page",
)


@callback(
    [
        Output("agg-total-chart", "figure"),
        Output("agg-sector-chart", "figure"),
        Output("agg-total-title", "children"),
        Output("agg-sector-title", "children"),
    ],
    [
        Input("agg-year", "value"),
        Input("agg-continent", "value"),
        Input("agg-gas", "value"),
        Input("agg-sectors", "value"),
    ],
)
def update_charts(year, continent, gas, sectors):
    """Fetch emissions data and update both charts."""
    continent_param = None if continent == "all" else continent
    sector_param = sectors if sectors else None

    data = get_emissions(
        year=year, gas=gas, continent=continent_param, sector=sector_param
    )

    month_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    # Color palette for sectors
    colors = [
        "#0d9488", "#f59e0b", "#ef4444", "#8b5cf6", "#3b82f6",
        "#ec4899", "#6366f1", "#14b8a6", "#f97316", "#84cc16",
    ]

    has_sector_filter = sectors and len(sectors) > 0

    # --- Total Emissions Line Chart ---
    total_fig = go.Figure()

    if data and has_sector_filter and "sectors" in data:
        # When sectors are filtered, sum only the selected sectors' timeseries
        sector_ts = data["sectors"].get("timeseries", [])
        monthly_totals = {}
        for entry in sector_ts:
            if entry["sector"] in sectors:
                month = entry["month"]
                monthly_totals[month] = monthly_totals.get(month, 0) + entry["emissionsQuantity"]

        if monthly_totals:
            sorted_months = sorted(monthly_totals.keys())
            x_labels = [month_labels[m - 1] for m in sorted_months]
            quantities = [monthly_totals[m] for m in sorted_months]

            total_fig.add_trace(
                go.Scatter(
                    x=x_labels,
                    y=quantities,
                    mode="lines+markers",
                    line=dict(color="#0d9488", width=2.5),
                    marker=dict(size=6, color="#0d9488"),
                    fill="tozeroy",
                    fillcolor="rgba(13, 148, 136, 0.08)",
                    hovertemplate="<b>%{x}</b><br>%{y:,.0f} tonnes<extra></extra>",
                )
            )
    elif data and "totals" in data:
        # No sector filter — use global totals
        timeseries = data["totals"].get("timeseries", [])
        months = [t["month"] for t in timeseries]
        quantities = [t["emissionsQuantity"] for t in timeseries]
        x_labels = [month_labels[m - 1] for m in months]

        total_fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=quantities,
                mode="lines+markers",
                line=dict(color="#0d9488", width=2.5),
                marker=dict(size=6, color="#0d9488"),
                fill="tozeroy",
                fillcolor="rgba(13, 148, 136, 0.08)",
                hovertemplate="<b>%{x}</b><br>%{y:,.0f} tonnes<extra></extra>",
            )
        )

    total_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Emissions (tonnes)",
        template="plotly_white",
        margin=dict(l=60, r=20, t=20, b=50),
        height=380,
        yaxis=dict(gridcolor="#f0f0f0"),
        xaxis=dict(gridcolor="#f0f0f0"),
    )

    # --- Second Chart: Bar (all sectors) or Line (filtered sectors) ---
    sector_fig = go.Figure()

    # Build titles
    continent_label = continent if continent != "all" else "All"

    if has_sector_filter:
        selected_label = ", ".join(s.replace("-", " ").title() for s in sectors)
        total_title = f"Total Emissions ({selected_label})"
        sector_title = f"Sector Emissions ({selected_label})"

        # Show a multi-line chart with each selected sector's monthly trend
        if data and "sectors" in data:
            sector_ts = data["sectors"].get("timeseries", [])
            for i, sector_key in enumerate(sectors):
                entries = sorted(
                    [e for e in sector_ts if e["sector"] == sector_key],
                    key=lambda e: e["month"],
                )
                if entries:
                    x_labels = [month_labels[e["month"] - 1] for e in entries]
                    y_vals = [e["emissionsQuantity"] for e in entries]
                    color = colors[i % len(colors)]
                    sector_fig.add_trace(
                        go.Scatter(
                            x=x_labels,
                            y=y_vals,
                            mode="lines+markers",
                            name=sector_key.replace("-", " ").title(),
                            line=dict(color=color, width=2.5),
                            marker=dict(size=6, color=color),
                            hovertemplate=(
                                "<b>%{fullData.name}</b><br>"
                                "%{x}: %{y:,.0f} tonnes<extra></extra>"
                            ),
                        )
                    )

        sector_fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Emissions (tonnes)",
            template="plotly_white",
            margin=dict(l=60, r=20, t=20, b=50),
            height=380,
            yaxis=dict(gridcolor="#f0f0f0"),
            xaxis=dict(gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        )
    else:
        total_title = f"Total Emissions ({continent})" if continent != "all" else "Total Emissions"
        sector_title = f"Sector Emissions ({continent})" if continent != "all" else "Sector Emissions (All)"

        # Show the bar chart with all sector summaries
        if data and "sectors" in data:
            summaries = data["sectors"].get("summaries", [])
            summaries_sorted = sorted(
                summaries, key=lambda s: s["emissionsQuantity"], reverse=True
            )

            sector_names = [
                s["sector"].replace("-", " ").title() for s in summaries_sorted
            ]
            sector_quantities = [s["emissionsQuantity"] for s in summaries_sorted]
            sector_percentages = [s["percentage"] for s in summaries_sorted]

            sector_fig.add_trace(
                go.Bar(
                    x=sector_quantities,
                    y=sector_names,
                    orientation="h",
                    marker_color=colors[: len(sector_names)],
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "%{x:,.0f} tonnes<br>"
                        "<extra></extra>"
                    ),
                    text=[f"{p:.1f}%" for p in sector_percentages],
                    textposition="auto",
                    textfont=dict(color="white", size=11),
                )
            )

        sector_fig.update_layout(
            xaxis_title="Emissions (tonnes)",
            template="plotly_white",
            margin=dict(l=180, r=20, t=20, b=50),
            height=380,
            yaxis=dict(autorange="reversed", gridcolor="#f0f0f0"),
            xaxis=dict(gridcolor="#f0f0f0"),
        )

    return total_fig, sector_fig, total_title, sector_title
