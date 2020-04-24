from collections import defaultdict
from datetime import MINYEAR, date

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from django.db.models import Max, Q, Sum, Case, When, Value, CharField
from django.utils import timezone
from django_plotly_dash import DjangoDash

from .models import Inventory, PPEType


def tabs_wrapper(n, title, vis_type):
    return dcc.Tab(
        label=title,
        id=f"tab{n}",
        value=f"Tab{n}",
        children=[
            dcc.Loading(
                id=f"loading{n}",
                type="default",
                children=[
                    html.Div(className="p-2 w-100 m-auto", id=f"tab{n}-{vis_type}")
                ],
            )
        ],
    )


app = DjangoDash("SimpleExample")

app.layout = html.Div(
    style={"width": "95%", "margin": "auto"},
    children=[
        html.Div(
            "",
            id="select-ppe-dropdown-message",
            className="d-inline-block text-primary m-3 text-left font-weight-bold w-100"
        ),
        dcc.Dropdown(
            placeholder="Select organization(s)",
            id="org-selector",
            options=[],
            multi=True,
            className="m-2",
        ),
        dcc.Dropdown(
            id=f"supply-picker",
            options=[
                {"label": "N95 Masks", "value": PPEType.N95MASK},
                {"label": "Gloves", "value": PPEType.GLOVES},
                {"label": "Rubbing Alcohol", "value": PPEType.ALCOHOL},
                {"label": "Swabs", "value": PPEType.SWAB},
                {"label": "Gowns", "value": PPEType.GOWNS},
                {"label": "Non-N95 Face Masks", "value": PPEType.FACE_MASK},
            ],
            clearable=False,
            placeholder="Select an item",
            className="m-2",
        ),
        html.Div(
            className="container-fluid row w-100 text-right",
            children=[
                html.Div(
                    "",
                    id="latest-update-notification",
                    className="col-10 d-inline-block text-primary m-1 d-col-6 text-center font-weight-bold"
                ),
                html.Div(
                    className="btn-group",
                    children=[
                        html.A(
                            "Download Data",
                            href="/dashboard/download?format=xlsx",
                            # type="button",
                            className="btn btn-primary"
                        ),
                        html.Button(
                            html.Span(
                                "Toggle Dropdown",
                                className="sr-only"
                            ),
                            type="button",
                            className="btn btn-primary dropdown-toggle dropdown-toggle-split",
                            **{
                                'data-toggle': 'dropdown',
                                'aria-haspopup': 'true',
                                'aria-expanded': 'false'
                            }
                        ),
                        html.Div(
                            className="dropdown-menu",
                            children=[
                                html.A(
                                    "Download Data (Excel)",
                                    href="/dashboard/download?format=xlsx",
                                    className="dropdown-item"
                                ),
                                html.A(
                                    "Download Data (.CSV)",
                                    href="/dashboard/download?format=csv",
                                    className="dropdown-item"
                                ),
                            ]
                        )
                    ]
                ),
            ],
        ),
        dcc.Tabs(
            id="tabs",
            value="Tab1",
            style={"font-family": "Arial, Helvetica, sans-serif"},
            className="m-2",
            children=[
                tabs_wrapper(1, "Table", "table"),
                tabs_wrapper(2, "Current Inventory", "graph"),
                tabs_wrapper(3, "Projected Daily Use", "graph"),
                tabs_wrapper(4, "Projected Days of Inventory Remaining", "graph"),
            ],
        ),
    ],
)


def parse_field_name(data, field_name):
    if "projected_run_out" not in field_name:
        y = [entry[field_name] for entry in data]
    else:
        y = []
        today = timezone.now().date()
        for entry in data:
            run_out_date = entry[field_name]
            if run_out_date:
                time_diff = run_out_date - today
                y.append(time_diff.days + time_diff.seconds / 3600)
            else:
                y.append(0)
    return y


def label_axis(field_name):
    if "projected_run_out" in field_name:
        return "Number of Days"
    return "Number of Items"


def provider_view(data, field_name):
    figure = go.Figure()
    str_format = "%a, %Y-%m-%d"
    x = [entry["timestamp"].strftime(str_format) for entry in data]
    figure.add_trace(
        go.Scatter(
            x=x,
            y=parse_field_name(data, field_name),
            mode="lines",
            line=dict(color="LightSkyBlue", width=4),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=x,
            y=parse_field_name(data, field_name),
            mode="markers",
            marker=dict(
                color="LightSkyBlue", size=15, line=dict(color="White", width=3)
            ),
        )
    )
    return figure


def admin_view(data, field_name):
    figure = go.Figure()
    str_format = "%a, %Y-%m-%d"
    x = [
        f"{entry['organization__name']}<br>{entry['timestamp__max'].strftime(str_format)}"
        for entry in data
    ]
    figure.add_trace(
        go.Bar(x=x, y=parse_field_name(data, field_name), marker_color="LightSkyBlue")
    )
    figure.update_layout()
    return figure


def create_figure(data, field_name, is_provider):
    if is_provider:
        return provider_view(data, field_name)
    return admin_view(data, field_name)


def callback_wrapper(selected_dropdown_label, orgs_selected, user, field_name):
    if user.organization.is_provider:
        # get the data
        pre_data = Inventory.objects.filter(
            organization=user.organization, ppetype__item_type=selected_dropdown_label,
        ).values("timestamp", field_name)

        # aggregate via sum using dictionary, unique keys as dates
        new_data = defaultdict(int)
        for i in pre_data:
            try:
                new_data[i["timestamp"].astimezone(tz=user.timezone).date()] += i[
                    field_name
                ]
            except TypeError:
                pass  # If grabs data points from a blank field, it just ignores the blank entry and moves on

        # reformat back into acceptable data format
        agg_data = [
            {"timestamp": key, field_name: value} for key, value in new_data.items()
        ]

        agg_data.sort(key=lambda x: x["timestamp"])

        figure = create_figure(agg_data, field_name, is_provider=True)
    else:
        if orgs_selected is None:
            providers = user.organization.get_descendants().filter(is_provider=True)
        else:
            providers = (
                user.organization.get_descendants()
                .filter(name__in=orgs_selected)
                .values("id")
            )
        max_data = (
            Inventory.objects.filter(
                organization__in=providers, ppetype__item_type=selected_dropdown_label
            )
            .values("organization")
            .annotate(Max("timestamp"))
            .order_by("organization")
        )

        if max_data.count():
            q_statement = Q()
            for max_row in max_data:
                q_statement = q_statement | (
                    Q(organization=max_row["organization"])
                    & Q(
                        timestamp__date=max_row["timestamp__max"]
                        .astimezone(tz=user.timezone)
                        .date()
                    )
                )
            data = (
                Inventory.objects.filter(ppetype__item_type=selected_dropdown_label)
                .filter(q_statement)
                .values("organization__name",)
                .annotate(Max("timestamp"))
                .annotate(Sum(field_name))
            )
            field_name = field_name + "__sum"
        else:
            # If we don't get any data in the above query, we need to render an empty graph
            data = Inventory.objects.none()
        figure = create_figure(data, field_name, is_provider=False)
    figure.update_layout(
        yaxis_title=label_axis(field_name),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        plot_bgcolor="rgba(207, 238, 252, 0.3)",
        font=dict(family="Arial, Helvetica, sans-serif", size=13),
    )
    return dcc.Graph(figure=figure)  # TODO: Resize, label, and stylize


@app.expanded_callback(
    Output("tab1-table", "children"),
    [Input("supply-picker", "value"), Input("org-selector", "value")],
)
def update_table(selected_dropdown_label, orgs_selected, **kwargs):
    columns = [
        {"name": "Organization", "id": "organization__name"},
        {"name": "Item Category", "id": "readable_ppe_type"},
        {"name": "Attribute", "id": "ppetype__item_attribute"},
        {"name": "Size", "id": "ppetype__size"},
        {"name": "Quantity", "id": "number"},
        {"name": "Daily Use", "id": "daily_use"},
        {"name": "Projected Daily Use", "id": "projected_daily_use"},
        {"name": "Projected Run-Out Date", "id": "projected_run_out"},
        {"name": "Date Submitted", "id": "timestamp__date"},
        {"name": "Comments", "id": "comments"},
    ]
    column_identifiers = [col["id"] for col in columns]
    user = kwargs["user"]
    if not user.organization:
        data = Inventory.objects.filter(
            user=user, ppetype__item_type=selected_dropdown_label
        )
    elif user.organization.is_provider:
        data = Inventory.objects.filter(
            organization=user.organization, ppetype__item_type=selected_dropdown_label
        )
    else:
        if orgs_selected is None:
            providers = user.organization.get_descendants().filter(is_provider=True)
        else:
            providers = (
                user.organization.get_descendants()
                .filter(name__in=orgs_selected)
                .values("id")
            )
        data = Inventory.objects.filter(
            organization__in=providers, ppetype__item_type=selected_dropdown_label
        ).select_related("ppetype")

    data = list(
        data.annotate(
            readable_ppe_type=Case(
                *[
                    When(ppetype__item_type=ppetype, then=Value(full_name))
                    for (ppetype, full_name) in PPEType.PPE_CHOICES
                ],
                default=Value("ppetype__item_type"),
                output_field=CharField(),
            )
        ).values(*column_identifiers)
    )

    style_data_conditional = []
    for index, row in enumerate(data[::-1]):
        try:
            if (row.get("projected_daily_use", 0) - row.get("daily_use", 0)) / row.get(
                "daily_use", 1
            ) > 0.5:
                style_data_conditional.append(
                    {
                        "if": {"row_index": index},
                        "backgroundColor": "#FF6848",
                        "color": "white",
                    }
                )
        except (TypeError, ZeroDivisionError):
            pass

    table = dash_table.DataTable(
        id="supply-table",
        columns=columns,
        data=data[::-1],
        style_as_list_view=True,
        style_header={
            "backgroundColor": "white",
            "fontWeight": "bold",
            "color": "black",
        },
        style_table={
            "maxHeight": "450px",
            "overflowY": "scroll",
            "border": "thin lightgrey solid",
        },
        style_cell={"padding": "0.5rem", "font-family": "sans-serif"},
        style_cell_conditional=style_data_conditional,
    )
    return table


@app.expanded_callback(
    Output("tab2-graph", "children"),
    [Input("supply-picker", "value"), Input("org-selector", "value")],
)
def update_current_inventory(selected_dropdown_label, orgs_selected, **kwargs):
    return callback_wrapper(
        selected_dropdown_label, orgs_selected, kwargs["user"], "number"
    )


@app.expanded_callback(
    Output("tab3-graph", "children"),
    [Input("supply-picker", "value"), Input("org-selector", "value")],
)
def update_projected_inventory(selected_dropdown_label, orgs_selected, **kwargs):
    return callback_wrapper(
        selected_dropdown_label, orgs_selected, kwargs["user"], "projected_daily_use"
    )


@app.expanded_callback(
    Output("tab4-graph", "children"),
    [Input("supply-picker", "value"), Input("org-selector", "value")],
)
def update_remaining_inventory(selected_dropdown_label, orgs_selected, **kwargs):
    user = kwargs["user"]
    field_name = "projected_run_out"

    if user.organization.is_provider:
        # get the data
        pre_data = Inventory.objects.filter(
            organization=user.organization, ppetype__item_type=selected_dropdown_label,
        ).values("timestamp", field_name)

        # aggregate using longest remaining date via a dictionary, unique keys as dates
        new_data = defaultdict(lambda: date(MINYEAR, 1, 1))
        for i in pre_data:
            try:
                temp = new_data[i["timestamp"].astimezone(tz=user.timezone).date()]
                new_data[i["timestamp"].astimezone(tz=user.timezone).date()] = (
                    i[field_name] if temp < i[field_name] else temp
                )
            except TypeError:
                pass  # If grabs data points from a blank field, it just ignores the blank entry and moves on

        # reformat back into acceptable data format
        agg_data = [
            {"timestamp": key, field_name: value} for key, value in new_data.items()
        ]

        agg_data.sort(key=lambda x: x["timestamp"])

        figure = create_figure(agg_data, field_name, is_provider=True)
    else:
        if orgs_selected is None:
            providers = user.organization.get_descendants().filter(is_provider=True)
        else:
            providers = (
                user.organization.get_descendants()
                .filter(name__in=orgs_selected)
                .values("id")
            )
        data = (
            Inventory.objects.filter(
                organization__in=providers, ppetype__item_type=selected_dropdown_label
            )
            .values("organization__name")
            .annotate(Max(field_name))
            .annotate(Max("timestamp"))
        )
        field_name = field_name + "__max"
        figure = create_figure(data, field_name, is_provider=False)
    figure.update_layout(
        yaxis_title=label_axis(field_name),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        plot_bgcolor="rgba(207, 238, 252, 0.3)",
        font=dict(family="Arial, Helvetica, sans-serif", size=13),
    )
    return dcc.Graph(figure=figure)  # TODO: Resize, label, and stylize


@app.expanded_callback(
    Output("select-ppe-dropdown-message",
           "children"), [Input("supply-picker", "value")]
)
def update__ppe_dropdown_message(selected_ppe_type, **kwargs):
    if not selected_ppe_type:
        return "Please use the drop-down selector to choose a type of PPE."
    return ""


@app.expanded_callback(
    Output("org-selector", "style"), [Input("org-selector", "value")]
)
def update_org_selector(selected_dropdown_label, **kwargs):
    # TODO: Populate selector with organizations
    user = kwargs["user"]
    if not user.organization:
        return {"display": "none"}
    elif not user.organization.is_provider:
        return {"display": "block"}
    return {"display": "none"}


@app.expanded_callback(
    Output("org-selector", "options"), [Input("org-selector", "value")]
)
def update_org_selector_options(selected_dropdown_label, **kwargs):
    user = kwargs["user"]
    return [
        {"label": i["name"], "value": i["name"]}
        for i in list(
            user.organization.get_descendants().filter(is_provider=True).values("name")
        )
    ]
