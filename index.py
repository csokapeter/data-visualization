from dash import Dash, dcc, html, Input, Output, callback
from app import app
from pages import final_results, cumulative_medals, medals_map, medals_per_capita_map

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/final-results':
        return final_results.layout
    elif pathname == '/cumulative-medals':
        return cumulative_medals.layout
    elif pathname == '/medals-map':
        return medals_map.layout
    elif pathname == '/medals-per-capita-map':
        return medals_per_capita_map.layout
    else:
        return html.Div([
            html.H1("Athletic Championship Visualizer"),
            html.Div([
                dcc.Link('Final results', href='/final-results'),
                html.Br(),
                dcc.Link('Cumulative medals', href='/cumulative-medals'),
                html.Br(),
                dcc.Link('Medals map', href='/medals-map'),
                html.Br(),
                dcc.Link('Medals per capita map', href='/medals-per-capita-map'),
            ]),
        ])

if __name__ == '__main__':
    app.run_server(debug=True)
