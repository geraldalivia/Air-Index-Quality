import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gdown

# Title page
st.set_page_config(page_title=" Air Quality Analysis by Geralda Livia")

# Title of the dashboard
st.title('Data Analysis Project: Air Quality Dashboard')

# Description
st.write('This is a dashboard that show analyzes air pollution data from Dongsi and Wanliu stations from 2013-2017, focusing on PM10 concentrations and meteorological factors')

# About me
st.markdown("""
### About Me
- **Name**: Geralda Livia Nugraha
- **Email Address**: mc299d5x1168@student.devacademy.id
- **Dicoding ID**: [MC299D5X1168](https://www.dicoding.com/users/alddar/)

### Project Overview
This project aims to analyze air quality data from Dongsi and Wanliu stations in China from 2013 to 2017, focusing on PM10 concentrations and Meteorological Parameter (TEMp, DEWP, and PRES) Effect.
This project provides a set of functions to visualize the hourly and monthly patterns of PM10 concentration in air quality data. The visualizations help in understanding the trends of air pollution across different time frames

### Define Question  
1. What is the daily pattern of PM10 concentrations at Dongsi and Wanliu stations for the period 2013-2017?
2. What are the specific effects of temperature (TEMP), dew point(DEWP), and air pressure (PRES) on PM10 at Dongsi and Wanliu stations over the past 12 months?        
""")


# Load Data from gdrive
file_id = "1--d07m7J4CniV6pfScx_S6sde5XJu05J"
output = "data.csv"
url = f'https://drive.google.com/uc?id={file_id}'

# Download data
@st.cache_data
def load_data():
    # Download file
    gdown.download(url, output, quiet=False)
    df = pd.read_csv(output)
    return df
try:
    data = load_data()
    st.write(f"Succes to load data {data.shape[0]} baris")
    st.dataframe(data.head())
except Exception as e:
    st.error(f"Error: {e}")

@st.cache
def load_data():
    df = pd.read_csv("Data_Dongsi_Wanliu.csv")

# Display raw data sample
with st.expander("Dataset Overview"):
    st.dataframe(data.head())
    st.write(f"Dataset shape: {data.shape}")
    
    # Display basic info
    col1, col2 = st.columns(2)
    with col1:
        st.write("Data Types:")
        st.write(data.dtypes)
    
    with col2:
        st.write("Missing Values:")
        missing_values = data.isnull().sum()
        missing_percentage = (data.isnull().sum() / len(data)) * 100
        missing_df = pd.DataFrame({
            'Missing Values': missing_values,
            'Percentage (%)': missing_percentage.round(2)
        })
        st.dataframe(missing_df)

# Data preprocessing
@st.cache_data
def preprocess_data(df):
    # Create datetime column
    if 'datetime' not in data.columns:
        df['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])
    
    # Extract time components
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['hour_of_day'] = df['datetime'].dt.hour
    df['month_name'] = df['datetime'].dt.month_name()
    df['year_month'] = df['datetime'].dt.strftime('%Y-%m')
    
    # Impute missing values
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for column in numeric_cols:
        if data[column].isnull().sum() > 0:
            data[column].fillna(data[column].median(), inplace=True)
    
    # Filter for stations of interest
    dongsi_data = df[df['station'] == 'Dongsi'].copy()
    wanliu_data = df[df['station'] == 'Wanliu'].copy()
    
    return df, dongsi_data, wanliu_data

# Preprocess data
df, dongsi_data, wanliu_data = preprocess_data(data)

# Sidebar for navigation
st.sidebar.title("Air Quality Analysis Dashboard")
options = st.sidebar.selectbox("Select Analysis", 
                               ["Daily PM10 Pattern", 
                                "Weather Effects on PM10", 
                                "Further Analysis", 
                                "Conclusion"])


# Daily PM10 Pattern
if options == "Daily PM10 Pattern":
    st.title("Daily PM10 Concentration Pattern (2013-2017)")
    
    # Filter data for the selected stations
    station = data['station'].value_counts()
    
    # Hourly average PM10
    hourly_pattern = data[data['station'] == station].groupby('hour')['PM10'].mean()
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_pattern.index, hourly_pattern.values, marker='o', label=station)
    plt.title(f'Daily Pattern of PM10 Concentration at {station} (2013-2017)')
    plt.xlabel('Hour')
    plt.ylabel('Average PM10')
    plt.xticks(range(24))
    plt.grid(True, alpha=0.3)
    plt.legend()
    st.pyplot(plt)

    st.info("""
    **Insights about PM10 Daily Patterns:**\n
    - Both stations show a pattern with two peaks. One in the morning (around 8-9 AM) and another in the evening (around 9-10 PM)\n
    - The evening peak was more pronounced, with PM10 levels reaching a maximum around 21:00 (9 PM), reaching values of around 130 at both stations. However, the lowest concentrations were recorded during the day between 13:00-15:00 (1-3 PM)\n
    - Dongsi and Wanliu stations show almost identical patterns, indicating that this phenomenon is regional and not just related to a particular location\n
    """)

    # Monthly average PM10
    hourly_pattern = data[data['station'] == station].groupby('month')['PM10'].mean()
    plt.figure(figsize=(12, 6))
    plt.plot(hourly_pattern.index, hourly_pattern.values, marker='o', label=station)
    plt.title(f'Daily Pattern of PM10 Concentration at {station} (2013-2017)')
    plt.xlabel('Hour')
    plt.ylabel('Average PM10')
    plt.xticks(range(24))
    plt.grid(True, alpha=0.3)
    plt.legend()
    st.pyplot(plt)

    st.info("""
    **Insights about PM10 Daily Patterns:**\n
    - Seasonal variation with highest concentrations in winter/spring (around 3rd month or March) and lowest in summer (around 8th month or August)\n
    - March shows peak concentrations (>140) at both stations, likely due to a combination of warming emissions and meteorological factors\n
    - The summer months (around 6th to 9th month or June-September) consistently show lower PM10 levels (<90), likely due to increased rainfall\n
    - Both stations show similar seasonal patterns, confirming the regional nature of air pollution\n
    """)



# Weather Effects on PM10
elif options == "Weather Effects on PM10":
    st.title("Weather Effects on PM10 Concentration")
    
    # Correlation analysis
    st.subheader("Correlation Heatmap")
    corr = data[['PM10', 'TEMP', 'DEWP', 'PRES']].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='YlGnBu', vmin=-1, vmax=1)
    plt.title('Correlation between PM10 and Weather Parameters')
    st.pyplot(plt)

    st.info("""
    **Insights about PM10 Daily Patterns:**\n
    - Temperature (TEMP) and Dew Point (DEWP) showed a negative correlation at both stations. For TEMP it is about -0.27 at Dongsi and -0.22 at Wanliu. For DEWP it is about -0.055 at Dongsi and -0.028 at Wanliu\n
    - Air Pressure (PRES) shows a weak positive correlation at both stations. About 0.074 at Dongsi and 0.029 at Wanliu\n
    """)

    # Scatter plots for interactive analysis
    st.subheader("Scatter Plots")
    meteo_factor = st.selectbox(
        "Select Meteorological Factor", 
        ["TEMP", "DEWP", "PRES"],
        key="meteo_dist"
    )
    fig = px.histogram(data, x=meteo_factor, color='station', nbins=50,
                      barmode='overlay', opacity=0.7,
                      title=f'Distribution of {meteo_factor} by Station',
                      labels={meteo_factor: meteo_factor, 'count': 'Frequency'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Temperature vs PM10
    st.write("PM10 vs Temperature")
    fig, ax = plt.subplots()
    sns.scatterplot(data=data, x='TEMP', y='PM10', hue='station', ax=ax)
    plt.title('PM10 vs Temperature')
    st.pyplot(fig)

    # Dew Point vs PM10
    st.write("PM10 vs Dew Point")
    fig, ax = plt.subplots()
    sns.scatterplot(data=data, x='DEWP', y='PM10', hue='station', ax=ax)
    plt.title('PM10 vs Dew Point')
    st.pyplot(fig)

    # Pressure vs PM10
    st.write("PM10 vs Pressure")
    fig, ax = plt.subplots()
    sns.scatterplot(data=data, x='PRES', y='PM10', hue='station', ax=ax)
    plt.title('PM10 vs Pressure')
    st.pyplot(fig)

    st.info("""
    **Insights about PM10 Daily Patterns:**\n
    - It is noted on the scatter plot of PM10 concentration and TEMP that PM10 concentration tends to increase when the temperature is below 0°C. In line with Temperature, Dew point (DEWP) also follows a similar pattern but with more scatter in its relationship\n
    - The air pressure (PRES) relationship is less clear, but there is a tendency for higher PM10 during high pressure systems\n
    - The similar patterns at both stations suggest that meteorological factors affect the entire region in the same way\n
    """)

# Further Analysis
elif options == "Further Analysis":
    st.title("Further Analysis Based on Temperature Categories")
    
    # Create temperature categories
    data['temp_category'] = pd.cut(data['TEMP'], bins=[-20, 0, 10, 20, 40], labels=['Cold (<0°C)', 'Cool (0-10°C)', 'Mild (10-20°C)', 'Warm (>20°C)'])
    
    # Group by temperature category and hour
    hourly_temp_pm10 = data.groupby(['station', 'temp_category', 'hour'])['PM10'].mean().reset_index()
    
    # Interactive selection for temperature category
    selected_temp_category = st.sidebar.selectbox("Select Temperature Category", ['Cold (<0°C)', 'Cool (0-10°C)', 'Mild (10-20°C)', 'Warm (>20°C)'])
    
    # Filter data based on selected temperature category
    filtered_data = hourly_temp_pm10[hourly_temp_pm10['temp_category'] == selected_temp_category]
    
    # Plotting
    plt.figure(figsize=(12, 6))
    for station in filtered_data['station'].unique():
        station_data = filtered_data[filtered_data['station'] == station]
        plt.plot(station_data['hour'], station_data['PM10'], marker='o', label=station)
    
    plt.title(f'PM10 Daily Pattern by Temperature Category: {selected_temp_category}')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average PM10')
    plt.grid(True, alpha=0.3)
    plt.legend()
    st.pyplot(plt)

    st.info("""
    **Insights about PM10 Daily Patterns:**\n
    - All temperature categories show similar patterns with peaks in the evening/night (around 6-10 PM) and troughs during the day (around 12-3 PM). This shows that apart from temperature, other factors such as daily human activities and atmospheric conditions affect PM10 concentrations\n
    - During the day, both stations with a temperature category of “Cold” showed a great decline around noon (around 12-3 PM), which formed a typical V-shaped pattern. This may indicate that even in cold weather, warmer daytime temperatures can temporarily improve air quality\n
    - The highest PM10 concentrations occur at night with a temperature category of “Cold” around 200 in Dongsi and 160 in Wanliu. This suggests that cold nighttime conditions create the worst air quality scenario\n
    - Both stations show similar patterns. However, Dongsi generally has higher PM10 concentrations under temperature conditions with the “Cold” category compared to Wanliu indicating possible site-specific factors affecting pollution dispersion\n
    - In the “Warm” temperature category, PM10 shows a stable graph throughout the day, with much less variation compared to the other temperature categories, suggesting that warmer conditions may result in more consistent air quality\n
    """)

# Conclusion
elif options == "Conclusion":
    st.title("Conclution Question 1 [What is the daily pattern of PM10 concentrations at Dongsi and Wanliu stations for the period 2013-2017?]")
    
    st.info("""
    **PM10 Daily Patterns**\n
    ****
    **Findings:**\n
    - Highest Point: Occurred at 21:00 (9 PM) with values of 130.3 in Dongsi and 129.7 in Wanliu\n
    - Lowest Point: Occurred at noon around 13:00-14:00 (1-2 PM) with values of 95.3 in Dongsi and 94.2 in Wanliu\n
    - Daily pattern: There are two peaks in a day (bi-modal pattern) - morning around 8-9 AM and evening around 21-22 PM\n
    **Reason:**\n
    - The morning peak coincides with the morning peak of transportation and industrial activities\n
    - The evening peak is due to a combination of afternoon/evening transportation activities and more stable atmospheric layer conditions at night (temperature inversion)\n
    - The low PM10 concentration during the day is likely due to the increased height of the atmospheric mixing layer and thermal turbulence that aids pollutant dispersion\n
    
    **Seasonal Patterns of PM10 Concentrations (2013-2017)**\n
    ****
    **Findings:**\n
    - Month with Highest PM10: March with values of 142.6 in Dongsi and 146.3 in Wanliu\n
    - Month with Lowest PM10: August with values of 73.8 in Dongsi and 78.2 in Wanliu\n
    - Seasonal Variations: Winter/semi-season (December-March) shows 30-50% higher PM10 concentrations than summer (June-August)\n
    **Reason:**\n
    - High PM10 concentrations in March are related to meteorological conditions\n
    - The low concentrations in summer (June-August) are attributed to heavy rainfall which helps to remove pollutants from the air (wet deposition)\n
    """)
    
    st.title("Conclusion Question 2 [What are the specific effects of temperature (TEMP), dew point(DEWP), and air pressure (PRES) on PM10 at Dongsi and Wanliu stations over the past 12 months?]")
    st.info("""
    **Effects of Weather Parameters on PM10 (Last 12 Months)**\n
    ****
    **Findings:**\n
    1. Temperature (TEMP)\n
        - Negative Correlation: -0.27 in  Dongsi and -0.22 in Wanliu\n
        - Highest PM10: Occurs when temperatures are below 0°C, reaching >150 in extremely cold conditions\n
        - PM10 Lows: Occurs when temperatures are 10-20°C (mild), with values around 70\n
    2. Dew Point (DEWP)\n
        - Weak Negative Correlation: -0.055 in Dongsi and -0.028 in Wanliu\n
        - Pattern: Similar to temperature but with a weaker correlation\n
    3. Air Pressure (PRES)\n
        - Weak Positive Correlation: 0.074 in Dongsi and 0.029 in Wanliu\n
        - Highest PM10: Seen in high pressure systems with values of 143.9 in Dongsi and 127.8 in Wanliu\n
    **Reason:**\n
    - Low temperatures are often associated with thermal inversions that trap pollutants near the ground surface\n
    - High pressure is usually associated with stable air and lack of atmospheric gas mixing, resulting in pollutants accumulating\n
    
    **Patterns by Temperature Category (Advanced Analysis)**\n
    ****
    **Findings:**\n
    - Cold Conditions (<0°C): Show the highest PM10 concentrations throughout the day, especially at night\n
    - Cool Conditions (0-10°C): Show similar daily patterns but with lower concentrations\n
    - Warm Conditions (>10°C): Shows significantly lower PM10 concentrations\n
    """)

    st.title("Recomendation related the Air Quality based on Analysis")
    st.info("""
    **Trafic**\n
    ****
    - Encourage the use of public transportation to reduce the use of private vehicles\n
    
    **Seasonality**\n
    ****
    - Improve monitoring and enforcement of industrial emissions during December-March when PM10 concentrations are highest\n
    - Develop an early warning system for air quality based on meteorological forecasts, especially during low temperature conditions\n
    - Implement operational restrictions on emission sources (private vehicles, heaters, etc.) during periods of cold air with high pressure\n
    
    **Energy Management**\n
    ****
    - Introduce and support programs to switch from vehicles with carbon-based fuels to renewable energy\n
            
    **Public Health Policy**\n
    ****  
    - Raise public awareness about the risks of PM10 exposure, especially during low temperatures and high pressures\n
    - Provide customized health recommendations for vulnerable groups (children, elderly, respiratory disease sufferers) based on identified daily and seasonal patterns\n
    """)
