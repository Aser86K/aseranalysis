import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State

data = (
    pd.read_csv('Sales.csv', encoding='ISO-8859-1')
    .assign(Date=lambda x: pd.to_datetime(x["date"]))
    .sort_values(by="Date")
)
shifts = data['shift'].sort_values().unique()
items = data['item_type'].sort_values().unique()
foods = data['item_name'].sort_values().unique()

external_stylesheets = [
    {
        "href": (
            "https://fonts.googleapis.com/css2?"
            "family=Montserrat:wght@400;700&display=swap"
        ),
        "rel": "stylesheet",
    },
    {
        "href": "aser_analytics/venv/assets/style.css", 
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = "Restaurant Data Analysis!"

custom_card_style = {
    "border": "1px solid #ccc",
    "border-radius": "5px",
    "padding": "3px",
    "margin": "1px",
    "width": "500px",  
    "height": "450px",
    "background-color": "black",
}

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🥗", className="header-emoji"),
                html.H1(
                    children="Restaurant Sales Analysis",
                    className="header-title",
                    style={"textAlign": "center", "fontSize": "48px", "color": "green"},
                ),
                html.P(
                    children="Sales DASHBOARD",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Shift", className="menu-title"),
                        dcc.Dropdown(
                            id="shift-filter",
                            options=[
                                {"label": shift, "value": shift}
                                for shift in shifts
                            ],
                            value="",
                            clearable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Food Category", className="menu-title"),
                        dcc.Dropdown(
                            id="food-category-filter",
                            options=[
                                {
                                    "label": item.title(),
                                    "value": item,
                                }
                                for item in items
                            ],
                            value="",
                            clearable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Food name", className="menu-title"),
                        dcc.Dropdown(
                            id="food-filter",
                            options=[
                                {
                                    "label": food,
                                    "value": food,
                                }
                                for food in foods
                            ],
                            value="",
                            clearable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["Date"].min().date(),
                            max_date_allowed=data["Date"].max().date(),
                            start_date=data["Date"].min().date(),
                            end_date=data["Date"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P("Total Revenue", className="card-title"),
                        html.H2(id="total-amount-value", className="card-value"),
                    ],
                    className="card-content",
                ),
                html.Div(
                    children=[
                        html.P("Online payment", className="card-title"),
                        html.H2(id="online-amount-value", className="card-value"),
                    ],
                    className="card-content",
                ),
                html.Div(
                    children=[
                        html.P("Cash payment", className="card-title"),
                        html.H2(id="cash-amount-value", className="card-value"),
                    ],
                    className="card-content",
                ),
            ],
            style={"display": "flex", "justify-content": "space-between"},
            className="card",
            id="total-amount-card",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="monthly-revenue-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(  
                    children=[
                        dcc.Graph(
                            id="profit-chart",
                            config={"displayModeBar": False},
                            style = custom_card_style,
                        ),
                        dcc.Graph(
                            id="food-chart",
                            config={"displayModeBar": False},
                            style = custom_card_style,
                        ),
                    ],
                    style = {"display": "flex", "flexDirection": "row", "justifyContent": "space-between",},
                    ),
                html.Div(  
                    children=[
                        dcc.Graph(
                            id="item-type-comparison-chart",
                            config={"displayModeBar": False},
                            style = custom_card_style,
                        ),
                        dcc.Graph(
                            id="shift-revenue-comparison-chart",
                            config={"displayModeBar": False},
                            style = custom_card_style,
                        ),
                    ],
                    style = {"display": "flex", "flexDirection": "row", "justifyContent": "space-between",},
                    ),
            ],
            className="wrapper",
        ),
    ]
)

     
@app.callback(
    Output("total-amount-value", "children"),
    Output("online-amount-value", "children"),
    Output("cash-amount-value", "children"),
    Output("profit-chart", "figure"),
    Output("monthly-revenue-chart", "figure"),
    Input("shift-filter", "value"),
    Input("food-category-filter", "value"),
    Input("food-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_total_amount_and_charts(selected_shift, selected_category, selected_food, start_date, end_date):
    filtered_data = data.query("Date >= @start_date and Date <= @end_date")

    if selected_shift:
        filtered_data = filtered_data.query("shift == @selected_shift")
    if selected_category:
        filtered_data = filtered_data.query("item_type == @selected_category")
    if selected_food:
        filtered_data = filtered_data.query("item_name == @selected_food")

    total_amount = filtered_data["transaction_amount"].sum()
    
    online_total_amount = filtered_data[filtered_data["transaction_type"] == "Online"]["transaction_amount"].sum()

    online_percentage = (online_total_amount / total_amount) * 100

    online_percentage_str = f"{online_percentage:.1f}%"
    
    cash_total_amount = filtered_data[filtered_data["transaction_type"] == "Cash"]["transaction_amount"].sum()

    cash_percentage = (cash_total_amount / total_amount) * 100

    cash_percentage_str = f"{cash_percentage:.1f}%"

    most_profitable_item = filtered_data.groupby('item_name')['transaction_amount'].sum().reset_index()
    most_profitable_item = most_profitable_item.sort_values('transaction_amount', ascending=False).head(10)
    top_profitable_item_name = most_profitable_item['item_name']
    top_item_profit = most_profitable_item['transaction_amount']

    monthly_revenue = filtered_data.resample("M", on="Date")["transaction_amount"].sum()
        
    annotations = [
                {
            "x": date,
            "y": amount,
            "xref": "x",
            "yref": "y",
            "text": f"${int(amount):,d}",
            "showarrow": True,
            "arrowhead": 0,
            "ax": 0,
            "ay": -40,
            "font": {"color": "white"},
                }
        for date, amount in zip(monthly_revenue.index, monthly_revenue)]
 
    profit_chart_figure = {
        "data": [
            {
                "x": top_profitable_item_name,
                "y": top_item_profit,
                "type": "bar",
                "text": [f"${int(amount):,d}" for amount in top_item_profit],
            },
        ],
        "layout": {
            "title": {
                "text": "Top Profitable Food",
                "x": 0.05,
                "xanchor": "left",
                "font": {"color": "white"},
            },
            "xaxis": {
                "fixedrange": True,
                "tickfont": {"color": "white"},
            },
            "yaxis": {
                "fixedrange": True,
                "tickprefix": "$",
                "tickfont": {"color": "white"},
            },
            "colorway": ["#158025"],
            "plot_bgcolor": "black",
            "paper_bgcolor": "black",
        }
    }
            
    monthly_revenue_chart_figure = {
        "data": [
            {
                "x": monthly_revenue.index,
                "y": monthly_revenue,
                "mode": "lines+markers",
                "line": {"shape": "spline"},
                "marker": {"size": 6},
            },
        ],
        "layout": {
            "title": {
                "text": "Monthly Revenue",
                "x": 0.05,
                "xanchor": "left",
                "font": {"color": "white"},
            },
            "xaxis": {
                "fixedrange": True,
                "tickfont": {"color": "white"},
            },
            "yaxis": {
                "fixedrange": True,
                "tickprefix": "$",
                "tickfont": {"color": "white"},
                "range": [0, max(monthly_revenue) + 1000] if not monthly_revenue.empty else [0, 1],
            },
            "colorway": ["#17b897"],
            "plot_bgcolor": "black",
            "paper_bgcolor": "black",
            "annotations": annotations,
        },
    }

    return f"${int(total_amount):,d}", f"${int(online_total_amount):,d} ({online_percentage_str})", f"${int(cash_total_amount):,d} ({cash_percentage_str})", profit_chart_figure, monthly_revenue_chart_figure


@app.callback(
    Output("food-chart", "figure"),
    Input("shift-filter", "value"),
    Input("food-category-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def food_chart(selected_shift, selected_category, start_date, end_date):
    filtered_data = data.query("Date >= @start_date and Date <= @end_date")

    if selected_shift:
        filtered_data = filtered_data.query("shift == @selected_shift")
    if selected_category:
        filtered_data = filtered_data.query("item_type == @selected_category")

    most_sold_item = filtered_data.groupby('item_name')['quantity'].sum().reset_index()
    most_sold_item = most_sold_item.sort_values('quantity', ascending=False).head(10)
    top_item_name = most_sold_item['item_name']
    top_item_quantities = most_sold_item['quantity']
    
    food_chart_figure = {
        "data": [
            {
                "x": top_item_name,
                "y": top_item_quantities,
                "type": "bar",
                "text": [f"{int(quantity):,d}" for quantity in top_item_quantities],
            },
        ],
        "layout": {
            "title": {
                "text": "Top Food Sold (Quantity)",
                "x": 0.05,
                "xanchor": "left",
                "font": {"color": "white"},
            },
            "xaxis": {
                "fixedrange": True,
                "tickfont": {"color": "white"},
            },
            "yaxis": {
                "fixedrange": True,
                "tickfont": {"color": "white"},
            },
            "colorway": ["#17b897"],
            "plot_bgcolor": "black",
            "paper_bgcolor": "black",
        }
    }
    return food_chart_figure

@app.callback(
    Output("item-type-comparison-chart", "figure"),
    Input("shift-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_item_type_comparison(selected_shift, start_date, end_date):
    filtered_data = data.query("Date >= @start_date and Date <= @end_date")

    if selected_shift:
        filtered_data = filtered_data.query("shift == @selected_shift")

    item_type_quantity = filtered_data.groupby("item_type")["quantity"].sum().reset_index()

    custom_colors = ["#FF5733", "#FFBD33"]
    
    item_type_comparison_figure = go.Figure(
        data=[
            go.Pie(
                labels=item_type_quantity["item_type"],
                values=item_type_quantity["quantity"],
                hole=0.3,
                textinfo="value+percent",
                marker=dict(colors=custom_colors),
            )
        ],
        layout={
            "title": "Item Type (Quantity Sold)",
            "colorway": px.colors.qualitative.Set3,
            "font": {"color": "white"},
            "plot_bgcolor": "black",
            "paper_bgcolor": "black",
        }
    )
    return item_type_comparison_figure  

@app.callback(
    Output("shift-revenue-comparison-chart", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_shift_comparison( start_date, end_date):
    filtered_data = data.query("Date >= @start_date and Date <= @end_date")
  
    shift_revenue = filtered_data.groupby("shift")["transaction_amount"].sum().reset_index()

    custom_colors = ["#33FFBD", "#33FF57", "#C7FF33", "#FF5733", "#FFBD33"]
    
    shift_revenue_comparison_figure = go.Figure(
        data=[
            go.Pie(
                labels=shift_revenue["shift"],
                values=shift_revenue["transaction_amount"],
                hole=0.3,
                textinfo="value+percent",
                marker=dict(colors=custom_colors),
            )
        ],
        layout={
            "title": "Shift Performance (Revenue $)",
            "colorway": px.colors.qualitative.Set3,
            "font": {"color": "white"},
            "plot_bgcolor": "black",
            "paper_bgcolor": "black",
            
        }
    )
    return shift_revenue_comparison_figure
    
@app.callback(
    Output("food-filter", "options"),
    Input("shift-filter", "value"),
    Input("food-category-filter", "value")
)
def update_food_options(selected_shift, selected_category):
    if selected_shift:
        filtered_data = data.query("shift == @selected_shift")
    else:
        filtered_data = data

    if selected_category:
        available_foods = filtered_data[filtered_data['item_type'] == selected_category]['item_name'].unique()
    else:
        available_foods = filtered_data['item_name'].unique()

    food_options = [{'label': food, 'value': food} for food in available_foods]

    return food_options

if __name__ == "__main__":
    app.run_server(debug=True)
