from dash import dcc, html, Input, Output, callback
import plotly.express as px
import numpy as np

from data import original_df, ioc_iso_df


def convert_placement_to_medal(position):
    medals = ['Gold', 'Silver', 'Bronze']
    return medals[int(position-1)]


color_map = {
    'Gold': 'gold',
    'Silver': 'silver',
    'Bronze': '#cd7f32'
}

ioc_to_iso_map = dict(zip(ioc_iso_df['ioc'], ioc_iso_df['iso']))

filtered_df = original_df.copy()
filtered_df = filtered_df[filtered_df['position'].isin([1,2,3])]
filtered_df['iso_country'] = filtered_df['country'].copy()
filtered_df['iso_country'] = filtered_df['iso_country'].apply(lambda x: ioc_to_iso_map.get(x, x))
filtered_df = filtered_df.groupby(['iso_country', 'country', 'position']).size().reset_index(name='count')
filtered_df['medal'] = filtered_df['position'].apply(convert_placement_to_medal)
medal_count = filtered_df.groupby('iso_country')['count'].sum()
filtered_df = filtered_df.merge(medal_count, on='iso_country')
filtered_df['log_count'] = np.log(filtered_df['count_y'])

fig = px.choropleth(
    filtered_df,
    locations='iso_country',
    locationmode='ISO-3',
    color='log_count',
    hover_data=['country', 'count_y']
)

actual_values = [int(np.e**val) for val in range(7)]
fig.update_coloraxes(colorbar_tickvals=list(range(7)), colorbar_ticktext=actual_values, colorbar_title='Number of medals')
fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Medals: %{customdata[1]}')
fig.update_layout(
   margin=dict(l=0, r=0, t=0, b=0),
   geo=dict(showcountries=True)
)


layout = html.Div(children=[
    html.H1(children='World Medals Map'),

    html.Div(children='''
        Map showing the number of medals won by each country.
    '''),
    html.Br(),
    dcc.Graph(
        id='world-map',
        figure=fig
    ),
    html.Br(),
    html.Div(id='hover-data-container'),
    html.Br(),
    dcc.Link('Go back to home page', href='/'),
    html.Br(),
    dcc.Link('Final results', href='/final-results'),
    html.Br(),
    dcc.Link('Cumulative medals', href='/cumulative-medals'),
    html.Br(),
    dcc.Link('Medals per capita map', href='/medals-per-capita-map')
])

@callback(
    Output('hover-data-container', 'children'),
    [Input('world-map', 'hoverData')]
)
def display_hover_data(hover_data):
    if hover_data is None:
        return 'Hover over a country to display medal distribution'

    country_name = hover_data['points'][0]['customdata'][0]
    country_data = filtered_df[filtered_df['country'] == country_name]

    pie_fig = px.pie(country_data, values='count_x', names='medal', color='medal', title=f'Medal Distribution for {country_name}', color_discrete_map=color_map)
    pie_fig.update_traces(textinfo='value')

    return dcc.Graph(figure=pie_fig)
