"""Emissions Sources — Main Dash application."""

import dash
from dash import Dash, html

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    title="Greenhouse Gas Emissions Dashboard",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {
            "name": "description",
            "content": "Visualize global greenhouse gas emissions data from Climate Trace",
        },
    ],
)

app.layout = html.Div(
    [
        dash.page_container,
        # Shared footer
        html.Footer(
            [
                html.P(
                    [
                        "Data Source: ",
                        html.A(
                            "Climate Trace",
                            href="https://climatetrace.org/data",
                            target="_blank",
                            rel="noopener noreferrer",
                            className="footer-link",
                        ),
                    ],
                    className="footer-source",
                ),
                html.P(
                    [
                        "Built with ",
                        html.Span("❤️"),
                        " by ",
                        html.A(
                            "Paul Otieno",
                            href="https://www.linkedin.com/in/paul-otieno-66740889/",
                            target="_blank",
                            rel="noopener noreferrer",
                            className="footer-link",
                        ),
                    ],
                    className="footer-credit",
                ),
            ],
            className="app-footer",
        ),
    ],
    className="app-container",
)

if __name__ == "__main__":
    app.run(debug=True)
