from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go

from data import original_df


def convert_placement_to_medal(position):
    medals = ['Gold', 'Silver', 'Bronze']
    return medals[int(position-1)]


layout = html.Div([
    dcc.Dropdown(
        id='sort_selector',
        options=[
            {'label': 'Sort by country name', 'value': 'country'},
            {'label': 'Sort by medal count', 'value': 'count'}
        ],
        value='country',
        clearable=False
    ),
    html.Br(),
    dcc.Dropdown(
        id='chart_type_selector',
        options=[
            {'label': 'Standard Stacked Bar Chart', 'value': 'standard'},
            {'label': 'Normalized Stacked Bar Chart', 'value': 'normalized'}
        ],
        value='standard',
        clearable=False
    ),
    dcc.Graph(id='medal_graph'),
    html.Br(),
    dcc.Link('Go back to home page', href='/'),
    html.Br(),
    dcc.Link('Final results', href='/final-results'),
    html.Br(),
    dcc.Link('Medals map', href='/medals-map'),
    html.Br(),
    dcc.Link('Medals per capita map', href='/medals-per-capita-map')
])

filtered_df = original_df.copy()
filtered_df = filtered_df[filtered_df['position'].isin([1,2,3])]
filtered_df = filtered_df.groupby(['country', 'position']).size().reset_index(name='count')
filtered_df['medal'] = filtered_df['position'].apply(convert_placement_to_medal)
total_medals = filtered_df.groupby('country')['count'].sum().rename('total_medals')
filtered_df['percentage'] = filtered_df.apply(lambda row: (row['count'] / total_medals[row['country']]) * 100, axis=1)

color_map = {
    'Gold': 'gold',
    'Silver': 'silver',
    'Bronze': '#cd7f32'
}


def sort_by_country(df):
    return df.sort_values(by=['country', 'count'], ascending=[True, False])


def sort_by_total_medals(df):
    return df.merge(total_medals, on='country').sort_values(by=['total_medals', 'country', 'medal'], ascending=[False, True, False])


def sort_by_medal_count(df, medal_type):
    medal_counts = df[df['medal'] == medal_type].groupby('country')['count'].sum().rename(f'{medal_type}_medal_count')
    return df.merge(medal_counts, on='country').sort_values(by=[f'{medal_type}_medal_count', 'country', 'medal'], ascending=[False, True, True])


def sort_by_medal_percentage(df, medal_type):
    medal_counts = df[df['medal'] == medal_type].groupby('country')['count'].sum().rename(f'{medal_type}_medal_count')
    medal_percentage = (medal_counts / total_medals * 100).rename(f'{medal_type}_percentage')
    return df.merge(medal_percentage, on='country').sort_values(by=[f'{medal_type}_percentage', 'country', 'medal'], ascending=[False, True, False])


@callback(
    Output('medal_graph', 'figure'),
    [Input('sort_selector', 'value'),
     Input('chart_type_selector', 'value')]
)
def update_graph(sort_by, chart_type):
    sort_logic = {
        'country': sort_by_country,
        'count': sort_by_total_medals,
        'gold_count': lambda df: sort_by_medal_count(df, 'Gold'),
        'silver_count': lambda df: sort_by_medal_count(df, 'Silver'),
        'bronze_count': lambda df: sort_by_medal_count(df, 'Bronze'),
        'gold_percentage': lambda df: sort_by_medal_percentage(df, 'Gold'),
        'silver_percentage': lambda df: sort_by_medal_percentage(df, 'Silver'),
        'bronze_percentage': lambda df: sort_by_medal_percentage(df, 'Bronze'),
    }
    sorted_df = sort_logic[sort_by](filtered_df)

    fig = go.Figure()

    medal_data = {'Gold': [], 'Silver': [], 'Bronze': []}

    for country in sorted_df['country'].unique():
        for medal in ['Gold', 'Silver', 'Bronze']:
            tmp_df = sorted_df[(sorted_df['country'] == country) & (sorted_df['medal'] == medal)]
            if not tmp_df.empty:
                medal_data[medal].append({
                    'x': tmp_df['country'].values[0],
                    'y': tmp_df['percentage'].values[0] if chart_type == 'normalized' else tmp_df['count'].values[0],
                    'customdata': tmp_df[['medal', 'count']].values[0],
                })
            else:
                medal_data[medal].append({
                    'x': country,
                    'y': 0,
                    'customdata': [country, 0]
                })

    for medal, data in medal_data.items():
        x_values = [d['x'] for d in data]
        y_values = [d['y'] for d in data]
        customdata = [d['customdata'] for d in data]
        hovertemplate = '<b>Country:</b> %{x}<br><b>Medal:</b> %{customdata[0]} <br><b>Count:</b> %{customdata[1]} <extra></extra>'
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=medal,
            marker_color=color_map[medal],
            customdata=customdata,
            hovertemplate=hovertemplate
        ))

    fig.update_layout(
        barmode='stack',
        xaxis_title='Country',
        title='Total number of medals by country' if chart_type == 'standard' else 'Percentage of different medals by country',
        yaxis_title='Number of medals' if chart_type == 'standard' else 'Percentage of medals'
    )

    return fig


@callback(
    Output('sort_selector', 'options'),
    Input('chart_type_selector', 'value')
)
def update_sort_options(chart_type):
    base_options = [
        {'label': 'Sort by country name', 'value': 'country'},
        {'label': 'Sort by total medal count', 'value': 'count'}
    ]
    if chart_type == 'standard':
        base_options.append({'label': 'Sort by gold count', 'value': 'gold_count'})
        base_options.append({'label': 'Sort by silver count', 'value': 'silver_count'})
        base_options.append({'label': 'Sort by bronze count', 'value': 'bronze_count'})
    elif chart_type == 'normalized':
        base_options.append({'label': 'Sort by percentage of gold medals', 'value': 'gold_percentage'})
        base_options.append({'label': 'Sort by percentage of silver medals', 'value': 'silver_percentage'})
        base_options.append({'label': 'Sort by percentage of bronze medals', 'value': 'bronze_percentage'})
    return base_options


@callback(
    Output('sort_selector', 'value'),
    Input('chart_type_selector', 'value')
)
def update_sort_value(chart_type):
    if chart_type == 'standard':
        return 'country'
    elif chart_type == 'normalized':
        return 'country'