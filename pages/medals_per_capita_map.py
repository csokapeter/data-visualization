from dash import dcc, html
import plotly.express as px
import numpy as np

from data import original_df, population_df, ioc_iso_df


def convert_placement_to_medal(position):
    medals = ['Gold', 'Silver', 'Bronze']
    return medals[int(position-1)]


ioc_to_iso_map = dict(zip(ioc_iso_df['ioc'], ioc_iso_df['iso']))

filtered_df = original_df.copy()
filtered_df = filtered_df[filtered_df['position'].isin([1,2,3])]
filtered_df['iso_country'] = filtered_df['country'].copy()
filtered_df['iso_country'] = filtered_df['iso_country'].apply(lambda x: ioc_to_iso_map.get(x, x))
filtered_df = filtered_df.merge(population_df, left_on='iso_country', right_on='iso3', how='left')
filtered_df = filtered_df.groupby(['iso_country', 'country', 'position']).size().reset_index(name='count')
filtered_df['medal'] = filtered_df['position'].apply(convert_placement_to_medal)
medal_count = filtered_df.groupby('iso_country')['count'].sum()
filtered_df = filtered_df.merge(population_df, left_on='iso_country', right_on='iso3', how='left')
filtered_df = filtered_df.merge(medal_count, on='iso_country')
filtered_df['medals_per_100k'] = (filtered_df['count_y'] / filtered_df['population']) * 100000
filtered_df['log_count_per_100k'] = np.log(filtered_df['medals_per_100k'])


fig = px.choropleth(
    filtered_df,
    locations='iso_country',
    locationmode='ISO-3',
    color='log_count_per_100k',
    hover_data=['country', 'medals_per_100k']
)

actual_values = [round(np.e**val, 4) for val in range(-8,3)]
fig.update_coloraxes(colorbar_tickvals=list(range(-8,3)), colorbar_ticktext=actual_values, colorbar_title='Number of medals')
fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Medals: %{customdata[1]}')
fig.update_layout(
   margin=dict(l=0, r=0, t=0, b=0),
   geo=dict(showcountries=True)
)


layout = html.Div(children=[
    html.H1(children='World Medals Map Per 100,000 person'),

    html.Div(children='''
        Map showing the number of medals won per 100,000 person by each country.
    '''),
    html.Br(),
    dcc.Graph(
        id='world-map-per-capita',
        figure=fig
    ),
    html.Br(),
    dcc.Link('Go back to home page', href='/'),
    html.Br(),
    dcc.Link('Final results', href='/final-results'),
    html.Br(),
    dcc.Link('Cumulative medals', href='/cumulative-medals'),
    html.Br(),
    dcc.Link('Medals map', href='/medals-map')
])
