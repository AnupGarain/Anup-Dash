from dash import Dash,html,dcc,Input,Output,dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app=Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server

df=px.data.gapminder()
topPopulation=df.groupby('country')['pop'].sum().nlargest(3).reset_index()
listCountry=df['country'].unique()

#Make card body
def makeCard(data):
    country=data["country"]
    population=data["pop"]
    card_content=[
        dbc.CardHeader(f"{country}"),
        dbc.CardBody([
            dcc.Markdown(dangerously_allow_html=True),
            f"{population}"])
    ]
    return card_content

#card callback function
#@app.callback(Output(cards,"children"),[Input(interval,"disable")])
def cardsData():
    populationCard=[]
    for index, row in topPopulation.iterrows():
        populationCard.append(makeCard(row))
    cardLayout=[
        dbc.Row([dbc.Col(card) for card in populationCard])
    ]
    return cardLayout

#live cards update
interval=dcc.Interval(interval=0)
cards=html.Div()

ScatterFig=px.scatter(data_frame=df,x="gdpPercap",y="lifeExp",size="pop",
               color="continent",hover_name="country",animation_frame="year")





#app layout
app.layout=dbc.Container([

    dbc.Row([
        dbc.Col([
            html.H1("Population Report",style={'textAlign':'center'})
        ])
    ]),
    dbc.Row([
       dbc.Container(cardsData(),className="my-5")
    ]),
    dbc.Row([
        dbc.Col([
          dcc.Graph(id='plot',figure=ScatterFig)
        ],width=6),
        dbc.Col([
          dcc.Dropdown(id='barplotInput',options=df['country'].unique(),value='China'),
          dcc.Graph(id='barplot')
        ],width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown([x for x in sorted(df.country.unique())], multi=True,placeholder='Filter by Country',id='country_drop')
        ], width=3),
        dbc.Col([
            dcc.Dropdown([x for x in sorted(df.continent.unique())],placeholder='Filter by Continent',id='continent_drop')
        ], width=3)]),
    dbc.Row([
        dash_table.DataTable(
            id='dataTable',
            data=df.to_dict('records'),
            columns=[{'id': c, 'name': c} for c in df.columns],
            editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="single",
            column_selectable="multi",
            row_selectable="multi",
            row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=6,
            style_cell={
                'minWidth': 95, 'maxWidth': 95, 'width': 95
            },
        )
    ])
])

@app.callback(
    Output(component_id='barplot',component_property='figure'),
    [Input(component_id='barplotInput',component_property='value')]
)
def barGraph(countryName):
    countryDataFrame=df[df['country']==countryName]

    BarChartfig = px.bar(countryDataFrame, x='year', y='pop',
                         hover_data=['lifeExp', 'gdpPercap'], color='year',
                         labels={'pop': f'population of {countryName}'}, height=400)
    return BarChartfig


@app.callback(
    Output('dataTable','data'),
    Input(component_id='continent_drop',component_property='value'),
    Input(component_id='country_drop',component_property='value')

)
def updatDataTable(continentData,countryData):
    updatedDF=df.copy()
    if continentData:
        updatedDF=updatedDF[updatedDF.continent==continentData]
    if countryData:
        updatedDF=updatedDF[updatedDF.country.isin(countryData)]

    return updatedDF.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
