import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="U.S. Agriculture & Climate Dashboard", layout="wide")

# ==========================================
# DATA LOADING & PREPROCESSING
# ==========================================

def convert_to_lbs(row):
    """Converts various agricultural units into standardized Pounds (LB) per Acre."""
    unit = row['UNIT']
    value = row['YIELD']
    crop = row['CROP']
    
    # Handle NaN values safely
    if pd.isna(value):
        return value
        
    if unit == 'TONS / ACRE':
        return value * 2000
    elif unit == 'LB / ACRE':
        return value
    elif unit == 'BU / ACRE':
        # Apply grain-specific weights
        weights = {
            'CORN': 56, 'SOYBEANS': 60, 'WHEAT': 60, 'OATS': 32,
            'BARLEY': 48, 'SORGHUM': 56, 'RYE': 56, 'FLAXSEED': 56
        }
        return value * weights.get(crop, 1) # Default to 1 if crop not in list
    return value

@st.cache_data
def load_data():
    # Load raw data
    corn_df = pd.read_csv('data/us_state_corn.csv')
    yield_df = pd.read_csv('data/us_state_crop_yield.csv')
    weather_df = pd.read_csv('data/us_state_monthly_weather.csv')

    # Ensure state names are uppercase for consistent merging
    corn_df['STATE'] = corn_df['STATE'].str.upper()
    yield_df['STATE'] = yield_df['STATE'].str.upper()
    weather_df['STATE'] = weather_df['STATE'].str.upper()

    # Dictionary to map full state names to 2-letter abbreviations for Plotly maps
    state_abbrev = {
        'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA', 
        'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA', 
        'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS', 
        'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD', 'MASSACHUSETTS': 'MA', 
        'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO', 'MONTANA': 'MT', 
        'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM', 
        'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK', 
        'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC', 
        'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT', 
        'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY'
    }
    
    corn_df['STATE_ABBR'] = corn_df['STATE'].map(state_abbrev)
    yield_df['STATE_ABBR'] = yield_df['STATE'].map(state_abbrev)
    weather_df['STATE_ABBR'] = weather_df['STATE'].map(state_abbrev)

    # Convert yield to numeric (removing commas)
    yield_df['YIELD'] = pd.to_numeric(yield_df['YIELD'].astype(str).str.replace(',', ''), errors='coerce')
    
    # Calculate standardized Yield in LBs
    yield_df['YIELD_LBS'] = yield_df.apply(convert_to_lbs, axis=1)
    
    # Pre-calculate Corn Revenue
    corn_df['REVENUE'] = corn_df['CORN_PRODUCTION_BU'] * corn_df['CORN_PRICE RECEIVED_$ / BU']

    return corn_df, yield_df, weather_df

# Load datasets
corn_df, yield_df, weather_df = load_data()
crops_available = sorted(yield_df['CROP'].dropna().unique())

# Month mapping for filters
month_names = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 
    7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'
}
month_options = list(month_names.values())
month_to_int = {v: k for k, v in month_names.items()}

# Helper function to get valid months list
def get_valid_months(plant_month_int, harvest_month_int):
    if plant_month_int <= harvest_month_int:
        return list(range(plant_month_int, harvest_month_int + 1))
    else:
        # Handles winter crops that cross over the new year (e.g. Nov to March)
        return list(range(plant_month_int, 13)) + list(range(1, harvest_month_int + 1))

st.title("🌾 U.S. Agriculture & Climate Trends Dashboard\nAuthor: Annan Zia")

# ==========================================
# 1. CROP YIELD GEOGRAPHIC DISTRIBUTION
# ==========================================
st.header("1. Geographic Crop Yield Viewer")
col1, col2 = st.columns(2)

with col1:
    selected_crop_map = st.selectbox("Select a Crop (Map)", crops_available, key='map_crop')

with col2:
    years_available = sorted(yield_df[yield_df['CROP'] == selected_crop_map]['YEAR'].dropna().unique(), reverse=True)
    selected_year_map = st.selectbox("Select a Year (Map)", years_available, key='map_year') if years_available else None

if selected_year_map:
    filtered_yield = yield_df[(yield_df['CROP'] == selected_crop_map) & (yield_df['YEAR'] == selected_year_map)]
    
    if not filtered_yield.empty:
        national_avg = filtered_yield['YIELD'].mean()
        unit = filtered_yield.iloc[0]['UNIT']
        
        # Metric
        st.metric(label=f"National Average Yield for {selected_crop_map} in {selected_year_map}", value=f"{national_avg:,.2f} {unit}")

        # Map
        fig_map = px.choropleth(
            filtered_yield,
            locations='STATE_ABBR',
            locationmode="USA-states",
            color='YIELD',
            scope="usa",
            hover_name="STATE",
            hover_data={'STATE_ABBR': False, 'YIELD': True, 'UNIT': True},
            color_continuous_scale="YlGn",
            title=f"Distribution of {selected_crop_map} Yield by State ({selected_year_map})",
            labels={'YIELD': f'Yield ({unit})'},
            height=700
        )
        st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ==========================================
# 2. YIELD TRENDS OVER TIME
# ==========================================
st.header("2. National Yield Trends Over Time")
selected_crops_multi = st.multiselect("Select Crops to Compare", crops_available, default=["CORN", "SOYBEANS"] if "CORN" in crops_available else [])

if selected_crops_multi:
    trend_data = yield_df[yield_df['CROP'].isin(selected_crops_multi)]
    
    # Check the native units of the selected crops
    unique_units = trend_data['UNIT'].dropna().unique()
    
    col_trend1, col_trend2 = st.columns([3, 1])
    with col_trend2:
        # If all crops have the SAME unit, let the user choose between that unit and LB / ACRE
        if len(unique_units) == 1:
            original_unit = unique_units[0]
            if original_unit == "LB / ACRE":
                unit_options = ["LB / ACRE"]
                is_disabled = True
            else:
                unit_options = [original_unit, "LB / ACRE"]
                is_disabled = False
        # If crops have DIFFERENT units, force standardized LB / ACRE and disable dropdown
        else:
            unit_options = ["LB / ACRE"]
            is_disabled = True
            st.info("Multiple crops with differing units selected. Chart locked to **LB / ACRE** for standardized comparison.")
            
        selected_unit = st.selectbox("Select Display Unit", unit_options, disabled=is_disabled, key="trend_unit")

    # Aggregate data based on unit selected
    if selected_unit == "LB / ACRE":
        trend_grouped = trend_data.groupby(['YEAR', 'CROP']).agg({'YIELD_LBS': 'mean'}).reset_index()
        y_col = 'YIELD_LBS'
        y_label = 'Average Yield (LB / ACRE)'
    else:
        trend_grouped = trend_data.groupby(['YEAR', 'CROP']).agg({'YIELD': 'mean', 'UNIT': 'first'}).reset_index()
        y_col = 'YIELD'
        y_label = f'Average Yield ({selected_unit})'

    fig_line = px.line(
        trend_grouped,
        x='YEAR',
        y=y_col,
        color='CROP',
        markers=True,
        title="Average Crop Yield Over Time",
        labels={y_col: y_label, 'YEAR': 'Year'},
        height=700 
    )
    
    col_spacer1, col_chart, col_spacer2 = st.columns([1, 4, 1])
    with col_chart:
        st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ==========================================
# 3. REVENUE CALCULATOR (CORN ONLY)
# ==========================================
st.header("3. Corn Revenue Calculator")
st.markdown("Calculates the historical value of corn based on total production and price per bushel.")

col_rev1, col_rev2 = st.columns(2)
with col_rev1:
    rev_years = sorted(corn_df['YEAR'].dropna().unique(), reverse=True)
    rev_year = st.selectbox("Select Year for Revenue", rev_years)

with col_rev2:
    rev_states = sorted(corn_df[corn_df['YEAR'] == rev_year]['STATE'].dropna().unique())
    rev_state = st.selectbox("Select State for Revenue", rev_states) if rev_states else None

if rev_state:
    rev_data = corn_df[(corn_df['YEAR'] == rev_year) & (corn_df['STATE'] == rev_state)]
    if not rev_data.empty:
        production = rev_data.iloc[0]['CORN_PRODUCTION_BU']
        price = rev_data.iloc[0]['CORN_PRICE RECEIVED_$ / BU']
        revenue = rev_data.iloc[0]['REVENUE']

        # Metrics with explicit units
        col_met1, col_met2, col_met3 = st.columns(3)
        col_met1.metric(label="Total Production", value=f"{production:,.0f} Bushels")
        col_met2.metric(label="Price Received", value=f"${price:,.2f} / BU")
        col_met3.metric(label="Calculated Revenue", value=f"${revenue:,.2f}")

st.divider()

# ==========================================
# 4. CLIMATE & YIELD CORRELATION HEATMAP
# ==========================================
st.header("4. Crop Climate Correlation Analyzer")
st.markdown("Discover the 'Sweet Spot' for a specific crop. This Density Heatmap shows the **Average Yield** for different combinations of Temperature and Precipitation. Look for the brightest yellow/green squares to find the optimal climate!")

col_scat1, col_scat2, col_scat3 = st.columns(3)
with col_scat1:
    selected_crop_scatter = st.selectbox("Select a Crop", crops_available, key='scatter_crop')
with col_scat2:
    plant_month_4 = st.selectbox("Planting Month", month_options, index=0, key='plant_4')
with col_scat3:
    harvest_month_4 = st.selectbox("Harvesting Month", month_options, index=11, key='harv_4')

if selected_crop_scatter:
    valid_months_4 = get_valid_months(month_to_int[plant_month_4], month_to_int[harvest_month_4])
    season_weather_4 = weather_df[weather_df['MONTH'].isin(valid_months_4)]
    
    weather_agg_4 = season_weather_4.groupby(['YEAR', 'STATE', 'STATE_ABBR']).agg({
        'PRECIPITATION': 'sum',
        'TEMP_AVG': 'mean'
    }).reset_index()

    crop_yield_data_4 = yield_df[yield_df['CROP'] == selected_crop_scatter]
    scatter_data = pd.merge(crop_yield_data_4, weather_agg_4, on=['YEAR', 'STATE', 'STATE_ABBR'], how='inner')
    
    if not scatter_data.empty:
        crop_unit = scatter_data['UNIT'].iloc[0] # Dynamically get the unit for the label

        fig_scatter = px.density_heatmap(
            scatter_data,
            x='TEMP_AVG',
            y='PRECIPITATION',
            z='YIELD',
            histfunc='avg',
            title=f"Yield Efficiency Heatmap based on {plant_month_4} - {harvest_month_4} Weather",
            labels={
                'TEMP_AVG': 'Avg Season Temp (°F)', 
                'PRECIPITATION': 'Total Season Precip (Inches)',
                'YIELD': f'Average Yield ({crop_unit})'
            },
            color_continuous_scale="Viridis",
            height=600,
            nbinsx=20, 
            nbinsy=20
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ========================================
# 5. INTERACTIVE OPTIMAL STATE FINDER MAP
# ========================================
st.header("5. Interactive Optimal State Finder Map")
st.markdown("Adjust the weather parameters based on the sweet spot you found above. The map will highlight states whose **historical average climate during the selected months** falls within your bounds.")
st.markdown("**Optimal (Green):** Meets BOTH Temp and Precip. **Semi-Optimal (Yellow):** Meets ONLY ONE condition. **Not Optimal (Grey):** Meets NEITHER condition.")

col_clim1, col_clim2, col_clim3 = st.columns(3)
with col_clim1:
    clim_crop = st.selectbox("Select Crop", crops_available, key='clim_crop')
with col_clim2:
    plant_month_5 = st.selectbox("Planting Month", month_options, index=0, key='plant_5')
with col_clim3:
    harvest_month_5 = st.selectbox("Harvesting Month", month_options, index=11, key='harv_5')

col_clim4, col_clim5 = st.columns(2)
with col_clim4:
    temp_range = st.slider("Optimal Temp Range (°F)", 50.0, 85.0, (63.0, 69.0), key='temp_slider')
with col_clim5:
    precip_range = st.slider("Optimal Precip Range (Inches)", 0.0, 60.0, (28.0, 34.0), key='precip_slider')

valid_months_5 = get_valid_months(month_to_int[plant_month_5], month_to_int[harvest_month_5])
season_weather_5 = weather_df[weather_df['MONTH'].isin(valid_months_5)]

weather_agg_5 = season_weather_5.groupby(['YEAR', 'STATE', 'STATE_ABBR']).agg({
    'PRECIPITATION': 'sum',
    'TEMP_AVG': 'mean'
}).reset_index()

crop_yield_data_5 = yield_df[yield_df['CROP'] == clim_crop]
clim_crop_data = pd.merge(crop_yield_data_5, weather_agg_5, on=['YEAR', 'STATE', 'STATE_ABBR'], how='inner')

if not clim_crop_data.empty:
    crop_unit_5 = clim_crop_data['UNIT'].iloc[0]

    state_climate_avg = clim_crop_data.groupby(['STATE', 'STATE_ABBR']).agg({
        'TEMP_AVG': 'mean',
        'PRECIPITATION': 'mean',
        'YIELD': 'mean'
    }).reset_index()

    # Determine which states meet the optimal parameters
    temp_met = (state_climate_avg['TEMP_AVG'] >= temp_range[0]) & (state_climate_avg['TEMP_AVG'] <= temp_range[1])
    precip_met = (state_climate_avg['PRECIPITATION'] >= precip_range[0]) & (state_climate_avg['PRECIPITATION'] <= precip_range[1])

    def determine_condition(t_met, p_met):
        if t_met and p_met:
            return "Optimal"
        elif t_met or p_met:
            return "Semi-Optimal"
        else:
            return "Not Optimal"

    state_climate_avg['CONDITION'] = [determine_condition(t, p) for t, p in zip(temp_met, precip_met)]

    # Format the hover data explicitly with units so it looks clean
    state_climate_avg['Avg Temp'] = state_climate_avg['TEMP_AVG'].apply(lambda x: f"{x:.1f} °F")
    state_climate_avg['Total Precip'] = state_climate_avg['PRECIPITATION'].apply(lambda x: f"{x:.1f} in")
    state_climate_avg['Avg Yield'] = state_climate_avg['YIELD'].apply(lambda x: f"{x:.1f} {crop_unit_5}")

    # Summary Metrics
    num_optimal = len(state_climate_avg[state_climate_avg['CONDITION'] == 'Optimal'])
    num_semi = len(state_climate_avg[state_climate_avg['CONDITION'] == 'Semi-Optimal'])
    
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("States in Optimal Zone", num_optimal)
    col_stat2.metric("States in Semi-Optimal Zone", num_semi)

    fig_clim_map = px.choropleth(
        state_climate_avg,
        locations='STATE_ABBR',
        locationmode='USA-states',
        color='CONDITION',
        scope='usa',
        color_discrete_map={
            "Optimal": "#2ca02c",       # Green
            "Semi-Optimal": "#ffd700",  # Yellow
            "Not Optimal": "#d3d3d3"    # Light Grey
        },
        hover_name='STATE',
        hover_data={
            'STATE_ABBR': False, 
            'CONDITION': False,
            'Avg Temp': True, 
            'Total Precip': True, 
            'Avg Yield': True
        },
        title=f"States with Optimal {plant_month_5} - {harvest_month_5} Climates for {clim_crop}",
        height=700
    )
    st.plotly_chart(fig_clim_map, use_container_width=True)