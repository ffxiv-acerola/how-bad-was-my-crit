import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html

dash.register_page(
    __name__,
    path="/compatibility",
)

data = [
    {
        "Expansion": "Dawntrail",
        "Category": "Ultimates",
        "Content": "FRU",
        "Supported": "✔",
    },
    {
        "Expansion": "Dawntrail",
        "Category": "Savage",
        "Content": "Light-heavyweight",
        "Supported": "✔",
    },
    {
        "Expansion": "Dawntrail",
        "Category": "Extreme trials",
        "Content": "EX1",
        "Supported": "✔",
    },
    {
        "Expansion": "Dawntrail",
        "Category": "Extreme trials",
        "Content": "EX2",
        "Supported": "✖",
    },
    {
        "Expansion": "Dawntrail",
        "Category": "Extreme trials",
        "Content": "EX3",
        "Supported": "✔",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Savage",
        "Content": "Asphodelos",
        "Supported": "✖",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Savage",
        "Content": "Abyssos",
        "Supported": "✖",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Savage",
        "Content": "Anabaseios",
        "Supported": "✔",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Extreme trials",
        "Content": "EX5 and earlier",
        "Supported": "✖",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Extreme trials",
        "Content": "EX6",
        "Supported": "✔",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Extreme trials",
        "Content": "EX7",
        "Supported": "✔",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Ultimates",
        "Content": "DSR",
        "Supported": "✖",
    },
    {
        "Expansion": "Endwalker",
        "Category": "Ultimates",
        "Content": "TOP",
        "Supported": "✖",
    },
]

# Convert to DataFrame
compatibility_df = pd.DataFrame(data)

# Order categories
category_order = ["Savage", "Extreme trials", "Ultimates"]
compatibility_df["Category"] = pd.Categorical(
    compatibility_df["Category"], categories=category_order, ordered=True
)
compatibility_df = compatibility_df.sort_values(["Expansion", "Category"])


# Generate dbc tables by expansion and category
def generate_tables_by_expansion(expansion: str) -> list:
    """
    Generate HTML tables showing content support status grouped by category.

    Args:
        expansion: Name of expansion to generate tables for

    Returns:
        List of HTML components containing category headers and tables

    Example:
        >>> tables = generate_tables_by_expansion("Dawntrail")
        >>> tables[0]  # First header
        <H4>Ultimates</H4>
    """
    tables = []
    exp_df = compatibility_df[compatibility_df["Expansion"] == expansion]
    for category in exp_df["Category"].unique():
        cat_df = exp_df[exp_df["Category"] == category][["Content", "Supported"]]
        tables.append(html.H5(category))
        table_rows = []
        for _, row in cat_df.iterrows():
            color = "#0f5132" if row["Supported"] == "✔" else "#58151c"
            table_rows.append(
                html.Tr(
                    [
                        html.Td(row["Content"], style={"width": "85%"}),
                        html.Td(
                            row["Supported"],
                            style={"width": "15%", "textAlign": "center"},
                        ),
                    ],
                    style={"backgroundColor": color, "color": "white"},
                )
            )
        tables.append(
            dbc.Table(
                [html.Tbody(table_rows)],
                bordered=True,
                dark=True,
                hover=True,
                responsive=True,
                striped=False,
                style={"marginBottom": "30px"},
            )
        )
    return tables


compatibility_div = html.Div(
    [
        html.H4("Dawntrail"),
        *generate_tables_by_expansion("Dawntrail"),
        html.H4("Endwalker"),
        *generate_tables_by_expansion("Endwalker"),
    ]
)


def layout():
    return html.Div(
        [
            html.H3("What fights are supported?"),
            html.P(
                "Both individual and party analyses are supported for the following encounters:"
            ),
            compatibility_div,
            html.B("All encounters from Shadowbringers and earlier are not supported."),
            html.P(
                "The major limiting factor affecting compatibility is correctly accounting for "
                "potencies and job mechanics for every single job, as these often change "
                "after job balancing/reworks/expansions. The current scope of this site "
                "is to support analyses for whatever content is currently relevant. "
                "Analyses will usually be accurate within an expansion, but might not be across "
                "expansions."
            ),
        ]
    )