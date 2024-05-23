# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Map class values to labels
spacex_df['class_label'] = spacex_df['class'].map({1: 'Success', 0: 'Failure'})

# Create a dash application
app = dash.Dash(__name__)

# Create the dropdown menu options
dropdown_options = [
    {'label': 'All Sites', 'value': 'ALL'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for launch site selection with default value 'ALL'
    html.Label("Select Launch Site:"), 
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        placeholder='Select a Site',
        value='ALL',  # Default value set to 'ALL'
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'}
    ),
    
    # Pie chart to show the total successful launches count for all sites
    dcc.Graph(id='success-pie-chart'),
    
    html.Br(),
    
    dcc.RangeSlider(id='payload-slider',min=min_payload, max=max_payload,step=1000,
    marks={int(min_payload): f'{int(min_payload)}', int(max_payload): f'{int(max_payload)}'},
    value=[min_payload, max_payload]),

    html.Br(),

    # Placeholder for scatter plot
    dcc.Graph(id='success-payload-scatter-chart'),

    html.Br(),

    # Placeholder for other components
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexWrap': 'wrap'})
])

# Callback function for the pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(location):
    if location == 'ALL':
        # Aggregate success counts by location
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        title = 'Success Counts by Launch Site'
        fig = px.pie(success_counts, 
                     values='count', 
                     names='Launch Site', 
                     title=title)
    else:
        # Filter the dataframe for the specific location
        location_data = spacex_df[spacex_df['Launch Site'] == location]
        total_success_failures = location_data.groupby('class_label').size().reset_index(name='count')
        title = f'Success and Failure Rates for {location}'
        fig = px.pie(total_success_failures, 
                     values='count', 
                     names='class_label', 
                     title=title)
    
    return fig

# Callback function for the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(location, payload_range):
    if location == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        title = 'Payload and Outcome Scatter Plot for All Sites'
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == location) & 
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        title = f'Payload and Outcome Scatter Plot for {location}'
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class_label', color='Booster Version Category', 
                     title=title)
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
