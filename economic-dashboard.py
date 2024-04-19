import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import base64
import dash_bootstrap_components as dbc

# Load the dataset
data = pd.read_csv('data.csv')

# Filter for South Korea
data_korea = data[data['Country Code'] == 'KOR']

# Filter for unemployment-related indicators
unemployment_keywords = ["Unemployment", "UEM"]  # Keywords to filter unemployment-related indicators
data_unemployment = data_korea[data_korea['Indicator Name'].str.contains('|'.join(unemployment_keywords), case=False)]

# Get unique unemployment indicators and years
unemployment_indicators = data_unemployment['Indicator Name'].unique().tolist()

# Load background image
background_image = base64.b64encode(open('./assets/world-map.svg', 'rb').read()).decode('ascii')

# Load logo image
logo_image = base64.b64encode(open('./assets/logo.svg', 'rb').read()).decode('ascii')

# Choose a Bootstrap theme
bootstrap_theme_url = dbc.themes.BOOTSTRAP  # or any other theme

# custom stylesheet
custom_stylesheet_url  = ['./assets/styles.css']

external_stylesheets = [bootstrap_theme_url, custom_stylesheet_url]

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Custom styles for the cards and graph margins
CARD_STYLE = {
    "backgroundColor": "#1C59A1",
    "borderRadius": "0.5rem",
    "margin": "10px",
    "padding": "10px",
    "color": "white",
    "boxShadow": "0px 0px 15px 5px rgba(0, 0, 0, 0.4)",
    "transition": "transform 0.25s ease, box-shadow 0.25s ease",  # Add transition for smooth hover effect
    "opacity": ".8",
    # "color": "#000428",

}

# Style for the custom card
CUSTOM_CARD_STYLE = {
    "backgroundColor": "white",
    "boxShadow": "0 3px 10px 0 rgba(99, 118, 129, 0.3)",
    "transition": "box-shadow 0.25s cubic-bezier(0.32, 0.01, 0, 1)",
    "cursor": "pointer",
    "borderRadius": "0.5rem",
    "position": "relative",
    "overflow": "hidden",
}


# Style for the graph cards to match the country cards reference
GRAPH_CARD_STYLE = {
    "backgroundColor": "rgba(255, 255, 255, 0.9)",
    "borderRadius": "0.5rem",
    "padding": "10px",
    "color": "white",
    "boxShadow": "0px 0px 15px 5px rgba(0, 0, 0, 0.4)",
        "marginBottom": "10px",  # Adjust margin as needed
}

# Define your color palette
color_palette = ['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099']

# You might want to create an overlay to achieve the glossy effect
GRAPH_CARD_OVERLAY_STYLE = {
    "position": "absolute",
    "top": "0",
    "left": "0",
    "height": "100%",
    "width": "100%",
    "backgroundImage": "linear-gradient(.36turn,#000428 3.34%,#3d51ff 114.07%)",
    "borderRadius": "inherit",  # To inherit the border radius from the card
}

# Navbar with logo
navbar = dbc.Navbar(
    [
      html.A(
          dbc.Row(
              [
                  dbc.Col(html.Img(src=f'data:image/svg+xml;base64,{logo_image}', height="80px"), className="align-self-center"),
              ],
              align="center",
              justify="start",  # Use "start", "center", "end", "between" or "around" here to adjust the alignment
          ),
          href="#"  # Link to the top of the page or your website home page
      ),
      dbc.NavbarBrand("South Korea Unemployment Analysis Dashboard", className="ms-auto me-auto", style={'color': 'white', 'fontSize': '28px'}),  # `ms-auto` and `me-auto` for centering in Bootstrap 5
    ],
    color="transparent",  # Set the navbar color to transparent
    dark=False,           # Set dark to False if you want a light navbar
    className="py-0",     # Reduce the padding on the y-axis for the navbar
    style={"height": "60px"},  # Set a fixed height for the navbar
)
# Function to generate custom cards
def generate_custom_card(id, title, content):
    card_body = dbc.CardBody(
        [
            html.H5(title, className="card-title"),
            html.P(content, className="card-text"),
        ]
    )
    # Adding 'animated-border-card' class to the card component
    return dbc.Card(card_body, id=id, className="animated-border-card", style=CUSTOM_CARD_STYLE)

# Function to apply a consistent layout to figures
def apply_fig_styles(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # Making plot background transparent
        paper_bgcolor='rgba(0,0,0,0)',  # Making paper background transparent
        font=dict(size=10),  # Adjusting font size
        margin=dict(l=20, r=20, t=40, b=20)  # Tightening figure margins
    )
    return fig
    
# Define a function to get the latest value of an indicator
def get_latest_value(indicator_name):
    indicator_data = data_unemployment[data_unemployment['Indicator Name'] == indicator_name]
    # Transpose the data to have years as rows
    indicator_data = indicator_data.melt(id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], var_name='Year', value_name='Value')
    # Convert year to numeric and sort to get the latest year
    indicator_data['Year'] = pd.to_numeric(indicator_data['Year'], errors='coerce')
    indicator_data = indicator_data.dropna(subset=['Year'])
    latest_year_data = indicator_data[indicator_data['Year'] == indicator_data['Year'].max()]
    if not latest_year_data.empty:
        latest_value = latest_year_data.iloc[0]['Value']
        return latest_value, int(latest_year_data.iloc[0]['Year'])
    return None, None

# Now create a card content generator function
def card_content(indicator_name, default_title="Key Indicator"):
    value, year = get_latest_value(indicator_name)
    if value is not None:
        return dbc.CardBody([
            html.H5(f"{indicator_name}", className="card-title"),
            html.P(f"{value}% in {year}", className="card-text")
        ])
    else:
        return dbc.CardBody([
            html.H5(f"{default_title}", className="card-title"),
            html.P("No data available", className="card-text")
        ])

# Function to generate card content with a shortened title
def card_content_short(indicator_name, default_title="Key Indicator"):
    value, year = get_latest_value(indicator_name)
    # Shortened titles
    short_titles = {
        "Unemployment, total (% of total labor force) (national estimate)": "Total Unemployment",
        "Unemployment, youth total (% of total labor force ages 15-24) (national estimate)": "Youth Unemployment",
        "Unemployment with advanced education (% of total labor force with advanced education)": "Advanced Education Unemployment",
        "Unemployment with intermediate education, female (% of female labor force with intermediate education)": "Education Unemployment, Female"
    }
    short_title = short_titles.get(indicator_name, default_title)
    
    if value is not None:
        return dbc.CardBody([
            html.H5(f"{short_title}", className="card-title"),
            html.P(f"{value}% in {year}", className="card-text")
        ])
    else:
        return dbc.CardBody([
            html.H5(f"{short_title}", className="card-title"),
            html.P("No data available", className="card-text")
        ])

# Update your key indicators row with the shortened titles
key_indicators_row = dbc.Row([
    dbc.Col(dbc.Card(card_content_short("Unemployment, total (% of total labor force) (national estimate)"), style=CARD_STYLE), md=3, lg=3),
    dbc.Col(dbc.Card(card_content_short("Unemployment, youth total (% of total labor force ages 15-24) (national estimate)"), style=CARD_STYLE), md=3, lg=3),
    dbc.Col(dbc.Card(card_content_short("Unemployment with advanced education (% of total labor force with advanced education)"), style=CARD_STYLE), md=3, lg=3),
    dbc.Col(dbc.Card(card_content_short("Unemployment with intermediate education, female (% of female labor force with intermediate education)"), style=CARD_STYLE), md=3, lg=3),
], className="mb-4")

# Use dbc.Container for overall layout, dbc.Row and dbc.Col for grid
app.layout = dbc.Container(fluid=True, style={
    'position': 'relative',
    'backgroundImage': 'linear-gradient(191.92deg, #000428 8.61%, #757DBE 192.04%)',
    'minHeight': '100vh',  # Ensure it covers the full viewport height
    'padding': '1.2em',
}, children=[
    # Simulated :before element for the animated background
    html.Div(style={
        'display': 'block',
        'position': 'fixed',
        'top': '2em',
        'left': '-100%',
        'right': '0',
        'bottom': '0',
        'backgroundImage': f'url("data:image/svg+xml;base64,{background_image}")',
        'backgroundRepeat': 'repeat-x',
        'backgroundPosition': 'center',
        'backgroundSize': 'auto 85vh',
        'pointerEvents': 'none',
        'userSelect': 'none',
        'animation': 'animatedgradient 32s linear infinite',
        'backfaceVisibility': 'hidden',
        'opacity': '0.5',
    }),
    navbar,
    # html.H1("South Korea Unemployment Dashboard",   style={'textAlign': 'center', 'color': 'white', 'fontSize': '28px'}),
    # Dropdown and slider
    dbc.Row([
        dbc.Col([
            html.Label("Select Unemployment Indicators", style={'marginTop': '1.2rem', 'color': 'white',}),
            dcc.Dropdown(
                id='indicator-dropdown',
                options=[{'label': i, 'value': i} for i in unemployment_indicators],
                value=unemployment_indicators[0] if unemployment_indicators else None,
                style={'width': '100%', 'color': 'black', 'marginTop': '.75rem'}
            ),
            html.Div([
                html.Label("Select Year Range", style={'marginBottom': '.5rem', 'marginLeft': '20px', 'color': 'white'}),
                dcc.RangeSlider(
                    id='year-range-slider',
                    min=1980,
                    max=2022,
                    step=1,
                    marks={year: str(year) for year in range(1980, 2023)},
                    value=[2010, 2022],
                    allowCross=False
                ),
            ], style={'marginTop': '1rem', 'marginBottom': '.5rem'}),
        ], width=12),
    ]),
    # Cards for key indicators
    key_indicators_row,
    # Graphs styled as cards
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='line-graph'), style=GRAPH_CARD_STYLE), width=4),
        dbc.Col(dbc.Card(dcc.Graph(id='bar-chart'), style=GRAPH_CARD_STYLE), width=5),
        dbc.Col(dbc.Card(dcc.Graph(id='scatter-plot', config={'displayModeBar': False}), style=GRAPH_CARD_STYLE), width=3),
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='heatmap'), style=GRAPH_CARD_STYLE), width=2),
        dbc.Col(dbc.Card(dcc.Graph(id='pie-chart'), style=GRAPH_CARD_STYLE), width=5),
        dbc.Col(dbc.Card(dcc.Graph(id='line-fig-variability'), style=GRAPH_CARD_STYLE), width=5),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id='area-plot'), style=GRAPH_CARD_STYLE), width=5),
        dbc.Col(dbc.Card(dcc.Graph(id='bubble-chart'), style=GRAPH_CARD_STYLE), width=4),
        dbc.Col(dbc.Card(dcc.Graph(id='histogram'), style=GRAPH_CARD_STYLE), width=3),
    ], className="mb-4"),
   
    html.Div(id='graph-message', className="text-center text-danger mt-2")
])

# Callback for updating graphs based on selected indicator and year
@app.callback(
    [
        Output('line-graph', 'figure'),
        Output('bar-chart', 'figure'),
        Output('scatter-plot', 'figure'),
        Output('pie-chart', 'figure'),
        Output('line-fig-variability', 'figure'),
        Output('histogram', 'figure'),
        Output('area-plot', 'figure'),
        Output('heatmap', 'figure'),
        Output('bubble-chart', 'figure'),
        Output('graph-message', 'children'),
    ],
    [
        Input('indicator-dropdown', 'value'),
        Input('year-range-slider', 'value')
    ]
)

def update_graphs(selected_indicator, selected_years):
    try:
        filtered_data = data_unemployment[data_unemployment['Indicator Name'] == selected_indicator]
        
        # Extract the years column based on the selected range
        years_column = [str(year) for year in range(selected_years[0], selected_years[1] + 1)]
        
        # Prepare data for plotting
        plot_data = pd.melt(filtered_data, id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], value_vars=years_column, var_name='Year', value_name='Value')

        # Filter data for South Korea and global or regional unemployment rate
        south_korea_data = data_unemployment[data_unemployment['Country Name'] == 'South Korea']
        global_or_regional_data = data_unemployment[data_unemployment['Country Name'] != 'South Korea']

        # Reshape the data for the line graph
        years_column = [str(year) for year in range(selected_years[0], selected_years[1] + 1)]
        sk_plot_data = pd.melt(south_korea_data, id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
                               value_vars=years_column, var_name='Year', value_name='Value')
        global_or_regional_plot_data = pd.melt(global_or_regional_data, id_vars=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code'], 
                                                value_vars=years_column, var_name='Year', value_name='Value')

        # Combine data for South Korea and global or regional unemployment rate
        combined_data = pd.concat([sk_plot_data, global_or_regional_plot_data])

        # Generate line graph for national trends comparison
        line_fig = px.line(
            combined_data, 
            x='Year', 
            y='Value', 
            title='Comparison with National Trends',
            labels={'Value': 'Unemployment Rate (%)', 'Year': 'Year'},
            color_discrete_sequence=['#757DBE']
        )

        # Apply consistent layout styles
        line_fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',  # Making plot background transparent
            paper_bgcolor='rgba(0,0,0,0)',  # Making paper background transparent
            font=dict(size=10),  # Adjusting font size
            margin=dict(l=20, r=20, t=40, b=20)  # Tightening figure margins
        )
        line_fig = apply_fig_styles(line_fig)

        # Bar Chart for comparing unemployment indicators in the selected year
        bar_fig = go.Figure()
        if not plot_data.empty:
          bar_fig = px.bar(
              plot_data,
              x='Year',
              y='Value',
              title=f'Unemployment Indicators from {selected_years[0]} to {selected_years[1]}',
              color_discrete_sequence=['#318F95']
          )
          bar_fig = apply_fig_styles(bar_fig)
        else:
            bar_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")
        
        plot_data = plot_data.dropna(subset=['Value'])

        # Scatter Plot comparing two unemployment indicators (assuming at least two are available)
        scatter_fig = go.Figure()

        if not plot_data.empty:
          scatter_fig = px.scatter(
              plot_data,
              x='Year',
              y='Value',
              size='Value',  # Adjusting the size of data points based on the value
              title='Comparison of Unemployment Trends Over Time',
              color_discrete_sequence=['#E64E44'],  # Using a continuous color scale
              labels={'Value': 'Unemployment Rate (%)'},  # Label for the size axis
              size_max=20,  # Maximum size of data points
          )
          scatter_fig = apply_fig_styles(scatter_fig)
        else:
            scatter_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")
        
        # Pie Chart for the distribution of unemployment indicators in the selected year
        pie_fig = go.Figure()
        if not plot_data.empty:
            pie_fig = px.pie(
                plot_data,
                values='Value',
                names='Year',
                title=f'Distribution of Unemployment Indicators from {selected_years[0]} to {selected_years[1]}',
                labels={'Value': 'Unemployment Rate (%)'}  # Label for the value axis
            )
            pie_fig.update_traces(hoverinfo='label+percent', textinfo='percent+label', textfont_size=14)
            pie_fig.update_layout(scene=dict(aspectmode="cube"))
            pie_fig = apply_fig_styles(pie_fig)       
        else:
            pie_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper") 

       # Line Chart showing variability of the selected indicator over years
        line_fig_variability = go.Figure()
        if not plot_data.empty:
            line_fig_variability = px.line(
                plot_data,
                x='Year',
                y='Value',
                title=f'Variability of {selected_indicator}',
                color_discrete_sequence=['#8B5A37']
            )
            line_fig_variability = apply_fig_styles(line_fig_variability)  
        else:
            line_fig_variability.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")


        # Histogram showing the distribution of values for the selected indicator
        hist_fig = go.Figure()
        if not plot_data.empty:
            hist_fig = px.histogram(
                plot_data,
                x='Value',
                title=f'Distribution of {selected_indicator}',
                color_discrete_sequence=color_palette
            )
            hist_fig = apply_fig_styles(hist_fig)    
        else:
          hist_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")  

        # Area Plot
        area_fig = go.Figure()
        if not plot_data.empty:
            area_fig = px.area(
                plot_data,
                x='Year',
                y='Value',
                title=f'Area Plot of {selected_indicator}',
                color_discrete_sequence=['#694BAF']
            )
            area_fig = apply_fig_styles(area_fig)  
        else:    
          area_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")  
  
        # Heatmap
        heatmap_fig = go.Figure()
        if not plot_data.empty:
            heatmap_fig = px.imshow(
                plot_data.pivot_table(index='Year', columns='Country Name', values='Value'),
                title='Unemployment by Country and Year'
                # No color_discrete_sequence as this is not a parameter for imshow
            )  
            heatmap_fig = apply_fig_styles(heatmap_fig)
        else:    
          heatmap_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")      
        
        # Bubble Chart
        bubble_fig = go.Figure()
        if not plot_data.empty:
            bubble_fig = px.scatter(
                plot_data,
                x='Year',
                y='Value',
                size='Value',
                color='Year',
                title='Unemployment Over Time',
                color_discrete_sequence=color_palette
            ) 
            bubble_fig = apply_fig_styles(bubble_fig)   
        else:    
          bubble_fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False, xref="paper", yref="paper")


        return line_fig, bar_fig, scatter_fig, pie_fig, line_fig_variability, hist_fig, area_fig, heatmap_fig, bubble_fig, None  # Return None for message div if no error occurs
    
    except Exception as e:
        # If an error occurs, display an error message
        error_message = html.Div([
            html.P(f"An error occurred: {str(e)}", className="alert alert-danger")
        ])
        return (
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            go.Figure(),
            error_message,
        )

# Callback to control the visibility of the graph plots based on whether an error message is displayed
@app.callback(
    [Output(component_id, 'style') for component_id in ['line-graph', 'bar-chart', 'scatter-plot', 'pie-chart', 'line-fig-variability', 'histogram', 'area-plot', 'heatmap', 'bubble-chart']],
    [Input('graph-message', 'children')]
)
def hide_graphs(error_message):
    if error_message:
        # If an error message is displayed, hide all graph plots
        return [{'display': 'none'}] * 9
    else:
        # If no error message, show all graph plots
        return [{'display': 'block'}] * 9

if __name__ == '__main__':
    app.run_server(debug=True)
