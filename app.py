import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the filtered data
jobs_df = pd.read_csv('filtered_jobs_with_cs_or_ai.csv')

# Mapping of state names to state codes
state_name_to_code = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    'District of Columbia': 'DC'
}

# Convert state names to state codes
jobs_df['state_code'] = jobs_df['location'].map(state_name_to_code)

# Define AI-related skills for the dropdown
ai_skills = ["Metadata", "Data Manipulation", "Data Science", "Machine Learning", "Big Data", "Apache Hadoop", "Apache Spark", "Artificial Intelligence", "Data Engineering", "Splunk"]

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("Average Pay by State, Degree Level, and Skill"),
    dcc.Dropdown(
        id='degree-level-dropdown',
        options=[
            {'label': 'Bachelor\'s degree', 'value': 'Bachelor\'s degree'},
            {'label': 'Master\'s degree', 'value': 'Master\'s degree'},
            {'label': 'Any', 'value': 'Any'},
            {'label': 'None', 'value': 'No Education Listed'}
        ],
        value='Any',  # Default value
        placeholder="Select a degree level"
    ),
    dcc.Dropdown(
        id='skills-dropdown',
        options=[{'label': skill, 'value': skill} for skill in ai_skills],
        value=ai_skills[0],  # Default value
        placeholder="Select a skill"
    ),
    dcc.Graph(id='us-map')
])

# Callback to update the map based on selected degree level and skill
@app.callback(
    Output('us-map', 'figure'),
    [Input('degree-level-dropdown', 'value'),
     Input('skills-dropdown', 'value')]
)
def update_map(selected_degree_level, selected_skill):
    if selected_degree_level == 'Any':
        filtered_df = jobs_df[jobs_df['skills'].str.contains(selected_skill, na=False)]
    else:
        filtered_df = jobs_df[(jobs_df['education_level'].str.contains(selected_degree_level, na=False)) &
                              (jobs_df['skills'].str.contains(selected_skill, na=False))]

    # Check if filtered data is empty
    if filtered_df.empty:
        print("No data available for the selected filters.")
        return px.choropleth(title="No data available for the selected filters.")

    # Calculate average pay by state
    state_avg_pay = filtered_df.groupby('state_code')['pay'].mean().reset_index()

    # Check if state_avg_pay is empty or has NaN values
    if state_avg_pay.empty or state_avg_pay['pay'].isnull().all():
        print("No valid pay data available for the selected filters.")
        return px.choropleth(title="No valid pay data available for the selected filters.")

    # Create a choropleth map
    fig = px.choropleth(
        state_avg_pay,
        locations='state_code',
        locationmode='USA-states',
        color='pay',
        scope='usa',
        labels={'pay': 'Average Pay'},
        title=f'Average Pay by State for {selected_degree_level} with {selected_skill}'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True) 