"""Home page — Landing page with navigation cards."""

import dash
from dash import html, dcc

dash.register_page(__name__, path="/", name="Home", title="Emissions Sources")

layout = html.Div(
    [
        # Hero section
        html.Div(
            [
                html.H1("Emissions Sources", className="hero-title"),
                html.P(
                    "Welcome to the emissions dashboard.",
                    className="hero-subtitle",
                ),
                html.P(
                    "Choose some data to visualize",
                    className="hero-instruction",
                ),
            ],
            className="hero-section",
        ),
        # Cards section
        html.Div(
            [
                # Card 1 — Sources Ranked by Emissions
                html.Div(
                    [
                        html.H3(
                            "Sources Ranked by Emissions",
                            className="card-title",
                        ),
                        html.P(
                            "Scatterbox map showing sources ranked by their emissions quantities.",
                            className="card-description",
                        ),
                        html.P(
                            "Annual data is available for 2021 through the current year.",
                            className="card-detail",
                        ),
                        dcc.Link(
                            [
                                html.Span("View Data"),
                                html.Span(" →", className="arrow"),
                            ],
                            href="/sources-ranked",
                            className="card-link",
                        ),
                    ],
                    className="nav-card",
                ),
                # Card 2 — Aggregate Emissions
                html.Div(
                    [
                        html.H3(
                            "Aggregate Emissions",
                            className="card-title",
                        ),
                        html.P(
                            "Get monthly aggregated emissions for a calendar year.",
                            className="card-description",
                        ),
                        html.P(
                            "Emissions can be filtered by year, gas, continent and sectors.",
                            className="card-detail",
                        ),
                        dcc.Link(
                            [
                                html.Span("View Data"),
                                html.Span(" →", className="arrow"),
                            ],
                            href="/aggregate-emissions",
                            className="card-link",
                        ),
                    ],
                    className="nav-card",
                ),
            ],
            className="cards-container",
        ),
    ],
    className="home-page",
)
