import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, HoverTool, TapTool, Slider, CustomJS, ColorBar, Div, TextInput, LabelSet
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256
from bokeh.layouts import column, row

# Load data
le_df = pd.read_csv("../Important DataFrames/le_df.csv")
trend_wins_df = pd.read_csv("../Important DataFrames/team_trend_win_percentages.csv")

# Get trendy and untrendy teams
trend_teams = []
trendy_teams = []
untrendy_teams = []
for season in le_df['Season'].unique():
    not_trend = list(le_df[le_df['Season'] == season].nlargest(5, 'Distance').get('Roster'))
    trend = list(le_df[le_df['Season'] == season].nsmallest(5, 'Distance').get('Roster'))
    trend_teams.extend(trend)
    trend_teams.extend(not_trend)
    trendy_teams.extend(trend)
    untrendy_teams.extend(not_trend)

# Create extremes dataframe
extremes_df = le_df[le_df['Roster'].isin(trend_teams)]
extremes_df = pd.merge(extremes_df, trend_wins_df, on='Roster')

# Create a ColumnDataSource for the full dataset
source = ColumnDataSource(extremes_df)

# Create a ColumnDataSource for filtered data
# Initialize with the first season's data to ensure points show on load
first_season = int(extremes_df['Season'].min())
first_season_data = extremes_df[extremes_df['Season'] == first_season]

filtered_source = ColumnDataSource(data=dict(
    LE_Component_1=list(first_season_data['LE_Component_1']),
    LE_Component_2=list(first_season_data['LE_Component_2']),
    Win_Percentage=list(first_season_data['Win_Percentage']),
    Roster=list(first_season_data['Roster']),
    Season=list(first_season_data['Season'])
))

# Calculate padding for the plot axes
x_padding = (extremes_df['LE_Component_1'].max() - extremes_df['LE_Component_1'].min()) * 0.1
y_padding = (extremes_df['LE_Component_2'].max() - extremes_df['LE_Component_2'].min()) * 0.1

# Create the figure with tooltips and tap tool included
p = figure(
    title='NBA Teams: Trends in Roster Height Distribution (2001-2024)',
    x_axis_label='Component 1 (Avg Height)',
    y_axis_label='Component 2 (Height Variance)',
    width=800,
    height=600,
    tools='pan,wheel_zoom,box_zoom,reset,save,tap,hover',
    x_range=(extremes_df['LE_Component_1'].min() - x_padding, extremes_df['LE_Component_1'].max() + x_padding),
    y_range=(extremes_df['LE_Component_2'].min() - y_padding, extremes_df['LE_Component_2'].max() + y_padding),
    tooltips=[
        ('Team', '@Roster'),
        ('Win %', '@Win_Percentage{0.000}')
    ]
)

# Style improvements
p.title.text_font_size = "16pt"
p.title.align = "center"
p.xaxis.axis_label_text_font_size = "14pt"
p.yaxis.axis_label_text_font_size = "14pt"
p.xaxis.major_label_text_font_size = "12pt"
p.yaxis.major_label_text_font_size = "12pt"
p.grid.grid_line_color = "#dddddd"
p.grid.grid_line_alpha = 0.6

# Define color mapper for win percentage
mapper = linear_cmap(
    field_name='Win_Percentage',
    palette=Viridis256,
    low=extremes_df['Win_Percentage'].min(),
    high=extremes_df['Win_Percentage'].max()
)

# Create scatter plot with enhanced selection appearance for better tap interaction
scatter = p.scatter(
    x='LE_Component_1',
    y='LE_Component_2',
    source=filtered_source,
    size=14,  # Slightly larger points for easier tapping
    alpha=0.8,
    color=mapper,
    legend_label='NBA Teams',
    selection_color='#ff0000',  # Red outline for selected points
    selection_alpha=1.0,        # Full opacity for selected points
    selection_line_width=3,     # Thicker outline for selected points
    selection_fill_alpha=1.0    # Full fill opacity when selected
)

# Add color bar
color_bar = ColorBar(
    color_mapper=mapper['transform'],
    width=10,
    location=(0, 0),
    title='Win %',
    title_text_font_size="12pt",
    major_label_text_font_size="10pt"
)
p.add_layout(color_bar, 'right')

# Style the legend
p.legend.location = "top_left"
p.legend.click_policy = "hide"
p.legend.label_text_font_size = "12pt"
p.legend.background_fill_alpha = 0.5

# Create a Div to display win percentage averages
averages_div = Div(
    text="""
    <div style="padding: 30px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #ddd; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
        <h2 style="text-align: center; color: #333; margin-bottom: 20px; font-family: 'Helvetica Neue', Arial, sans-serif;">Win Percentage Analysis</h2>
        
        <div style="margin-bottom: 15px;">
            <h3 style="color: #2c3e50; font-size: 16px; margin-bottom: 5px;">Trendy Teams</h3>
            <div style="background-color: #e8f4f8; padding: 10px; border-radius: 5px; border-left: 4px solid #3498db;">
                <p style="font-size: 20px; font-weight: bold; color: #3498db; margin: 0;">N/A</p>
                <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">Teams with shorter, more uniform rosters</p>
            </div>
        </div>
        
        <div style="margin-bottom: 15px;">
            <h3 style="color: #2c3e50; font-size: 16px; margin-bottom: 5px;">Trend-Defying Teams</h3>
            <div style="background-color: #fef5e7; padding: 10px; border-radius: 5px; border-left: 4px solid #e67e22;">
                <p style="font-size: 20px; font-weight: bold; color: #e67e22; margin: 0;">N/A</p>
                <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">Teams with taller, more diverse rosters</p>
            </div>
        </div>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed #ccc;">
            <p style="font-size: 14px; color: #555; text-align: center; font-style: italic;">Use the slider to explore different seasons</p>
        </div>
    </div>
    """,
    width=350,
    height=400
)

# Create a slider for season filtering
slider = Slider(
    start=int(extremes_df['Season'].min()),
    end=int(extremes_df['Season'].max()),
    value=int(extremes_df['Season'].min()),
    step=1,
    title="Season",
    bar_color="#3498db",
    height=50,
    width=650
)

# Create a text input for entering a specific season
text_input = TextInput(
    value=str(int(extremes_df['Season'].min())),
    title="Enter Season:",
    width=130
)

# Create JavaScript callback to filter data and update stats
callback = CustomJS(args=dict(
    source=source,
    filtered_source=filtered_source,
    slider=slider,
    text_input=text_input,
    trendy_teams=trendy_teams,
    untrendy_teams=untrendy_teams,
    averages_div=averages_div
), code="""
    const season = parseInt(slider.value);
    const data = source.data;
    const filtered_data = {
        LE_Component_1: [],
        LE_Component_2: [],
        Win_Percentage: [],
        Roster: [],
        Season: []
    };
    
    // Arrays to store win percentages for trendy and untrendy teams
    let trendy_win_pcts = [];
    let untrendy_win_pcts = [];
    let trendy_rosters = [];
    let untrendy_rosters = [];
    
    for (let i = 0; i < data['Season'].length; i++) {
        if (data['Season'][i] === season) {
            filtered_data['LE_Component_1'].push(data['LE_Component_1'][i]);
            filtered_data['LE_Component_2'].push(data['LE_Component_2'][i]);
            filtered_data['Win_Percentage'].push(data['Win_Percentage'][i]);
            filtered_data['Roster'].push(data['Roster'][i]);
            filtered_data['Season'].push(data['Season'][i]);
            
            // Check if team is in trendy_teams for this season
            if (trendy_teams.includes(data['Roster'][i])) {
                trendy_win_pcts.push(data['Win_Percentage'][i]);
                trendy_rosters.push(data['Roster'][i]);
            }
            
            // Check if team is in untrendy_teams for this season
            if (untrendy_teams.includes(data['Roster'][i])) {
                untrendy_win_pcts.push(data['Win_Percentage'][i]);
                untrendy_rosters.push(data['Roster'][i]);
            }
        }
    }
    
    // Calculate averages
    let trendy_avg = 0;
    if (trendy_win_pcts.length > 0) {
        trendy_avg = trendy_win_pcts.reduce((a, b) => a + b, 0) / trendy_win_pcts.length;
    }
    
    let untrendy_avg = 0;
    if (untrendy_win_pcts.length > 0) {
        untrendy_avg = untrendy_win_pcts.reduce((a, b) => a + b, 0) / untrendy_win_pcts.length;
    }
    
    // Create roster lists
    let trendy_list = trendy_rosters.join(', ');
    let untrendy_list = untrendy_rosters.join(', ');
    
    // Format win percentages
    const trendy_pct = (trendy_avg * 100).toFixed(1) + '%';
    const untrendy_pct = (untrendy_avg * 100).toFixed(1) + '%';
    
    // Update the HTML div with the averages
    averages_div.text = `
    <div style="padding: 30px; background-color: #f8f9fa; border-radius: 10px; border: 1px solid #ddd; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
        <h2 style="text-align: center; color: #333; margin-bottom: 20px; font-family: 'Helvetica Neue', Arial, sans-serif;">Season ${season} Analysis</h2>
        
        <div style="margin-bottom: 15px;">
            <h3 style="color: #2c3e50; font-size: 16px; margin-bottom: 5px;">Trendy Teams</h3>
            <div style="background-color: #e8f4f8; padding: 10px; border-radius: 5px; border-left: 4px solid #3498db;">
                <p style="font-size: 20px; font-weight: bold; color: #3498db; margin: 0;">${trendy_pct}</p>
                <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">Teams with shorter, more uniform rosters</p>
            </div>
            <p style="font-size: 11px; color: #777; margin-top: 5px; line-height: 1.3; height: 40px; overflow: auto;">${trendy_list}</p>
        </div>
        
        <div style="margin-bottom: 15px;">
            <h3 style="color: #2c3e50; font-size: 16px; margin-bottom: 5px;">Trend-Defying Teams</h3>
            <div style="background-color: #fef5e7; padding: 10px; border-radius: 5px; border-left: 4px solid #e67e22;">
                <p style="font-size: 20px; font-weight: bold; color: #e67e22; margin: 0;">${untrendy_pct}</p>
                <p style="font-size: 12px; color: #666; margin: 5px 0 0 0;">Teams with taller, more diverse rosters</p>
            </div>
            <p style="font-size: 11px; color: #777; margin-top: 5px; line-height: 1.3; height: 40px; overflow: auto;">${untrendy_list}</p>
        </div>
        
        <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed #ccc;">
            <p style="font-size: 14px; color: #555; text-align: center; font-style: italic;">Win % difference (Trendy - Trend-Defying): ${((trendy_avg - untrendy_avg) * 100).toFixed(1)}%</p>
        </div>
    </div>
    `;
    
    // Update filtered source
    filtered_source.data = filtered_data;
    filtered_source.change.emit();
    
    // Update text input to match slider
    text_input.value = String(season);
""")

# Connect callback to slider
slider.js_on_change('value', callback)

# Create callback for text input
text_input_callback = CustomJS(args=dict(
    slider=slider,
    text_input=text_input,
    min_season=int(extremes_df['Season'].min()),
    max_season=int(extremes_df['Season'].max())
), code="""
    // Parse entered season
    let season = parseInt(text_input.value);
    
    // Validate the entered season
    if (isNaN(season)) {
        console.log("Invalid season");
        return;
    }
    
    // Ensure season is within bounds
    if (season < min_season) {
        season = min_season;
        text_input.value = String(min_season);
    } else if (season > max_season) {
        season = max_season;
        text_input.value = String(max_season);
    }
    
    // Update slider with new value
    slider.value = season;
""")

# Connect text input to callback
text_input.js_on_change('value', text_input_callback)

# Create the layout with slider and text input in the same row
controls = row(slider, text_input)
layout = column(
    controls,
    row(p, averages_div)
)

# Output to static HTML file
output_file("nba_height_trends_interactive.html", title="NBA Height Trends Analysis")

# Save the visualization with simple HTML output
save(layout)

print("Visualization saved as 'nba_height_trends_interactive.html'")