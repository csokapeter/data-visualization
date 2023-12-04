from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from datetime import datetime

from data import original_df


def convert_time_to_seconds(time_str):
    formats = ['%H:%M:%S', '%M:%S', '%M:%S.%f', '%S.%f']
    matched_fmt = ''
    for fmt in formats:
        try:
            datetime.strptime(time_str, fmt)
            matched_fmt = fmt
        except:
            continue

    if matched_fmt == '%H:%M:%S':
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        return time_obj.hour * 60 * 60 + time_obj.minute * 60 + time_obj.second
    elif matched_fmt == '%M:%S':
        time_obj = datetime.strptime(time_str, '%M:%S')
        return time_obj.minute * 60 + time_obj.second
    elif matched_fmt == '%M:%S.%f':
        time_obj = datetime.strptime(time_str, '%M:%S.%f')
        return time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000
    elif len(time_str.split('.')) > 1:
        time_obj = time_str.split('.')
        return int(time_obj[0]) + int(time_obj[1]) / 100


first_placements = original_df.copy()
first_placements['time_seconds'] = original_df['mark'].apply(convert_time_to_seconds)


layout = html.Div([
    html.H2('Final results over time'),
    dcc.Checklist(
        id='display-all-events-checkbox',
        options=[{'label': 'Display all events', 'value': 'ALL'}],
        value=['ALL']
    ),

    dcc.Graph(id='time-series-chart'),

    html.Br(),
    dcc.Link('Go back to home page', href='/'),
    html.Br(),
    dcc.Link('Cumulative medals', href='/cumulative-medals'),
    html.Br(),
    dcc.Link('Medals map', href='/medals-map'),
    html.Br(),
    dcc.Link('Medals per capita map', href='/medals-per-capita-map')
])


@callback(
    Output('time-series-chart', 'figure'),
    [Input('display-all-events-checkbox', 'value')]
)
def update_graph(checkbox_values):
    is_visible = True if 'ALL' in checkbox_values else 'legendonly'
    fig = go.Figure()

    for selected_event in original_df['event'].unique():
        for sex in original_df['sex'].unique():
            df_by_event_and_sex = first_placements[(first_placements['event'] == selected_event) & (first_placements['sex'] == sex) & (first_placements['position'] == 1)]
            custom_data = df_by_event_and_sex[['event', 'name', 'mark']]
            if not df_by_event_and_sex.empty:
                line_style = 'dash' if sex.lower() == 'women' else 'dot' if sex.lower() == 'mixed' else 'solid'
                hovertemplate = '<b>Event:</b> %{customdata[0]} <br> <b>Year:</b> %{x}<br><b>Name:</b> %{customdata[1]} <br><b>Result:</b> %{customdata[2]} <extra></extra>'

                fig.add_trace(go.Scatter(
                    x=df_by_event_and_sex['year'], 
                    y=df_by_event_and_sex['time_seconds'], 
                    mode='lines+markers',
                    name=f"{selected_event} - {sex}",
                    line=dict(dash=line_style),
                    hovertemplate=hovertemplate,
                    customdata=custom_data,
                    visible=is_visible
                ))

    fig.update_layout(
        title='Best results for all events over the years',
        plot_bgcolor='white',
        xaxis=dict(
            gridcolor='#C8C8C8'  # Light grey grid lines for the x-axis
        ),
        yaxis=dict(
            gridcolor='#C8C8C8'  # Light grey grid lines for the y-axis
        )
    )
        

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
