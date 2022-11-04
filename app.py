import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date, datetime

# Read in the data
data_file = r'C:\Users\Marco\Documents\Finances\Casa\precio_trimestral_apartamentos.csv'
data = pd.read_csv(data_file, index_col='Month')
data.index = pd.to_datetime(data.index)
district_cols = data.columns.insert(0, 'All Districts')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'Apartment Prices in Lima'
server = app.server

app.layout = html.Div(
    id="app-container",
    style={'padding': '3rem 16rem 8rem 16rem'},
    children=[
        html.Div(
            id="header-area",
            children=[
                html.H1(
                    id="header-title",
                    children='Apartment Prices in Lima by Districts'),
                html.P(
                    children='This application allows you to look at individualized apartment prices '
                             'in the city of Lima. You are able to filter by districts, and set a specific '
                             'timeframe.'
                )
            ],
            style={
                "margin-bottom": "30px",
            }
        ),
        html.Div(
            id="menu-area",
            children=[
                dbc.Row([
                    dbc.Col(
                        [
                            html.H5(
                                className="menu-title",
                                children='District'
                            ),
                            dcc.Dropdown(
                                id="district-filter",
                                className="dropdown",
                                options=[{"label": district, "value": district} for district in district_cols],
                                value='All Districts',
                                clearable=False,
                                disabled=False
                            )
                        ],
                        width=dict(size=3, offset='auto')
                    ),
                    dbc.Col(
                        [
                            html.H5(
                                className="menu-title",
                                children="Date Range"
                            ),
                            dcc.DatePickerRange(
                                id="date-range",
                                display_format='MMM YYYY',
                                initial_visible_month=date(2015, 8, 5),
                                min_date_allowed=data.index.min().date(),
                                max_date_allowed=data.index.max().date(),
                                start_date=data.index.min().date(),
                                end_date=data.index.max().date(),
                                disabled=True
                            )
                        ],
                        width=dict(size=3, offset='auto')
                    ),
                ]
                ),
                dbc.Col(
                    dbc.Button('Search',
                               id='button-search',
                               # color='primary',
                               n_clicks=0)
                    ,
                    width=dict(size=4, offset='auto')
                )
            ]
            ,
            style={
                "margin-bottom": "40px",
            }
        ),
        dbc.Row([
            dbc.Col([
                html.H4(
                    id='district-header',
                    children=['District Data:']
                ),
                html.H2(
                    id='district-name',
                    children=''
                ),
                html.H6(
                    id='district-info',
                    children='Please select a district for more information'
                ),
                html.H3(
                    id='district-return',
                    children=''
                )
            ],
                width=dict(size=3, offset=0)
            ),
            dbc.Col(
                id="graph-container",
                children=dcc.Graph(
                    id="price-chart",
                    figure=px.line(data),
                    config={"displayModeBar": False}
                ),
                width=dict(size=9, offset='austo')
            )
        ])
    ]
)


@app.callback(
    Output(component_id="price-chart", component_property="figure"),
    Input(component_id='button-search', component_property='n_clicks'),
    State(component_id="district-filter", component_property="value"),
    State(component_id="date-range", component_property="start_date"),
    State(component_id="date-range", component_property="end_date")
)
def update_chart(_, district, start_date, end_date):
    """Updates the graph for the district selected"""
    # filtered_data = data.loc[(data.index >= start_date) & (data.index <= end_date)]
    if district == 'All Districts':
        filtered_data = data
    else:
        filtered_data = data[district]
    fig = px.line(
        filtered_data,
    )
    fig.update_layout(
        yaxis_title="USD/m2",
        xaxis_title=None,
        legend_title=''
    )
    return fig


@app.callback(
    Output(component_id="district-name", component_property='children'),
    Output(component_id="district-info", component_property='children'),
    Output(component_id="district-return", component_property='children'),
    Input(component_id='button-search', component_property='n_clicks'),
    State(component_id="district-filter", component_property="value")
)
def update_district_info(_, district):
    """Updates basic information aboue the district selected"""
    if district == 'All Districts':
        district = ''
        no_years = 'Please select a district for more information'
        perc_return = ''
    else:
        district = str(district)
        filtered_data = data[district]
        percent, years = calculate_returns(filtered_data)
        no_years = 'Return of investment in {} years is'.format(years)
        perc_return = '{}%'.format(percent)

    return district, no_years, perc_return


def calculate_returns(df):
    """Calculates the percernt return over period of time"""
    df = df.dropna(how='all')
    start_date = df.index.min()
    end_date = df.index.max()
    start_price = df.loc[start_date]
    end_price = df.loc[end_date]
    perc = round((end_price - start_price) / start_price * 100, 0)
    years = len(pd.date_range(start=start_date, end=end_date, freq='Y'))
    return perc, years


if __name__ == "__main__":
    app.run_server(debug=True)
