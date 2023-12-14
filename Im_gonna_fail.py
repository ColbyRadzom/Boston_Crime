"""CS-230 Final Project. Analyzing a data set of crime in Boston. By Colby Radzom. My code makes a pie chart of the
 different categories of the day when crimes occur. Makes a stacked bar chart showing number of crimes that occur each
 day of the week for months. A bar chart showing the numbers of a variety of different crimes. Finally, makes a map of
 where the different crimes take place"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pyd
import altair as alt
import calendar
import numpy as np

st.set_option('deprecation.showPyplotGlobalUse', False)  # don't get stupid error message
SLIDER_VALUE = 30


def setup():
    # Activate Streamlit
    st.title("Crimes in Boston 2023")
    st.subheader("By Colby Radzom")

    # Read in Data
    crimes = pd.read_csv("bostoncrime2023_7000_sample.csv")
    dfcrimes = pd.DataFrame(crimes)
    return dfcrimes


def crimetimeentertainment(dfcrimes):
    # Calculate the crimes that took place at different times of the day
    st.write("What would you like to explode on the Pie Chart?")
    time_of_day = st.selectbox("Time Options", ["Morning (5AM-12AM)", "Afternoon(12PM-5PM)", "Evening(5PM-9PM)",
                                                "Night(9PM-5AM)"])
    explode = (0, 0, 0, 0)
    if time_of_day == "Morning (5AM-12AM)":
        explode = (0.1, 0, 0, 0)
    elif time_of_day == "Afternoon(12PM-5PM)":
        explode = (0.0, 0.1, 0, 0)
    elif time_of_day == "Evening(5PM-9PM)":
        explode = (0, 0, 0.1, 0)
    elif time_of_day == "Night(9PM-5AM)":
        explode = (0, 0, 0, 0.1)  # set up choosing system to explode
    st.subheader("Pie Chart of Crimes that occur at the different parts of the day")
    crimetime = dfcrimes["HOUR"]
    morning_range = (crimetime >= 5) & (crimetime < 12)  # make ranges for time of day
    afternoon_range = (crimetime >= 13) & (crimetime < 17)
    evening_range = (crimetime >= 18) & (crimetime < 21)
    night_range = ((crimetime >= 0) & (crimetime < 5)) | ((crimetime >= 22) & (crimetime <= 23))
    dfcategories = pd.DataFrame({"Time Category": ["Morning", "Afternoon", "Evening", "Night"],
                                 "Occurrences": [morning_range.sum(), afternoon_range.sum(), evening_range.sum(),
                                                 night_range.sum()]})
    plt.axis("equal")
    dfcategories.plot(kind="pie", y="Occurrences", labels=dfcategories["Time Category"],
                      startangle=0, explode=explode, autopct="%1.1f%%", shadow=True, legend=False)
    st.pyplot()  # make plot


def crimemonth_day(dfcrimes):
    # Histogram of Crimes per day per month
    # Have an option to change looking at number of crimes per day of the week or per month
    # Stacked bar chart of days a crime is committed in a month
    # Python where happiness comes to die

    st.subheader("Stacked Bar graph of Monthly Crimes")

    columns = ["MONTH", "Day of the Week", "Number of Crimes Committed"]
    crime_crime = pd.DataFrame(columns=columns)  # make a new Data Frame with the above columns

    # Loop through each month and day of the week
    week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for month in range(1, 12):  # January to November
        for day in week:
            # Finds crimes committed each week day each month by checking month and day
            crime_filtered = dfcrimes[(dfcrimes["MONTH"] == month) & (dfcrimes["DAY_OF_WEEK"] == day)]
            num_crimes = len(crime_filtered)  # number of crimes on respective day
            crime_crime = crime_crime._append(
                {"MONTH": calendar.month_name[month], "Day of the Week": day,
                 "Number of Crimes Committed": num_crimes}, ignore_index=True)  # Append a row to the DataFrame
    # Creates stacked bar graph with months and then weeks inside the bars
    bar_chart = alt.Chart(crime_crime, title="Weekday makeup of crimes committed each month").mark_bar().encode(
        x=alt.X("MONTH:N", title="Month", sort=list(calendar.month_name)),  # sorts the calendar dates
        y=alt.Y("sum(Number of Crimes Committed):Q", title="Number of Crimes Committed"),
        color=alt.Color("Day of the Week:N", title="Day of the Week", sort=week))
    st.altair_chart(bar_chart, use_container_width=True)  # use_cont... makes the bars automatically size themselves


def crime_variety(dfcrimes, slider_value=30):
    # Make a dictionairy of all the crime descriptions to replace
    crimereplace = {'ASSAULT - AGGRAVATED': 'ASSAULT', 'ASSAULT - SIMPLE': 'ASSAULT',
    "AUTO THEFT - MOTORCYCLE / SCOOTER": "AUTO THEFT", "AUTO THEFT - LEASED/RENTED VEHICLE": "AUTO THEFT",
    "BURGLARY - RESIDENTIAL": "BURGLARY", "BURGLARY - COMMERCIAL": "BURGLARY",
    "DRUGS - POSSESSION/ SALE/ MANUFACTURING/ USE": "DRUGS", 'FRAUD - FALSE PRETENSE / SCHEME': 'FRAUD',
    'FRAUD - CREDIT CARD / ATM FRAUD': 'FRAUD', 'FRAUD - WIRE': 'Fraud', 'FRAUD - WELFARE': 'Fraud',
    'FORGERY / COUNTERFEITING': 'FRAUD', 'FRAUD - IMPERSONATION': 'FRAUD',
    'LARCENY THEFT FROM MV - NON-ACCESSORY': 'THEFT', 'LARCENY SHOPLIFTING': 'THEFT',
    'LARCENY THEFT OF MV PARTS & ACCESSORIES': 'THEFT', 'LARCENY THEFT FROM BUILDING': 'THEFT',
    'LARCENY THEFT OF BICYCLE': 'THEFT', 'M/V ACCIDENT - PROPERTY DAMAGE': 'VEHICLE ACCIDENT',
    'M/V ACCIDENT - OTHER': 'VEHICLE ACCIDENT', 'M/V ACCIDENT - OTHER CITY VEHICLE': 'VEHICLE ACCIDENT',
    'M/V ACCIDENT - PERSONAL INJURY': 'VEHICLE ACCIDENT',
    'M/V ACCIDENT - INVOLVING PEDESTRIAN - INJURY': 'VEHICLE ACCIDENT',
    'M/V ACCIDENT - INVOLVING BICYCLE - INJURY': 'VEHICLE ACCIDENT',
    "MURDER, NON-NEGLIGENT MANSLAUGHTER": "MURDER"}
    # Replace alternative names with standardized names
    dfcrimes["OFFENSE_DESCRIPTION"] = dfcrimes['OFFENSE_DESCRIPTION'].replace(crimereplace)
    crime_counts = dfcrimes['OFFENSE_DESCRIPTION'].value_counts()  # counts number of occurrences of each crime descr.
    st.subheader("Bar graph showing the number of each type of crime")
    st.write("Decide the Minimum Counts of Crimes: Default value is", slider_value)
    slider_value = st.number_input("Minimum counts of Crimes:", value=slider_value)
    popularcrimes = crime_counts[crime_counts > slider_value]
    # Make a bar chart of the counts of different types of crimes committed
    fig, ax = plt.subplots(figsize=(40, 24))
    popularcrimes.plot(kind='bar', color='skyblue')
    plt.title('Number of Counts for Each Offense Description', fontsize=60)
    plt.xlabel('Offense Description', fontsize=50)
    plt.ylabel('Count', fontsize=50)
    plt.xticks(rotation=45, ha='right', fontsize=30)
    plt.yticks(fontsize=30)
    # Display the chart in Streamlit
    st.pyplot(fig)
    return dfcrimes, crime_counts


def crimeplace(dfcrimes, crime_counts):
    st.header("Map of Crimes in Boston")
    dfdirections = dfcrimes["Location"].str.strip("()")                               \
                       .str.split(", ", expand=True)                   \
                       .rename(columns={0: "Latitude", 1: "Longitude"})  # Stack Overflow Adding Lat Lon coordinates to
    # separate columns (python/dataframe)
    dfdirections["Offense_Code"] = dfcrimes["OFFENSE_CODE"]
    dfdirections["Offense_Description"] = dfcrimes["OFFENSE_DESCRIPTION"]
    dfdirections["Street"] = dfcrimes["STREET"]
    dfdirections["Occured_on_Date"] = dfcrimes["OCCURRED_ON_DATE"]
    columns = ["Latitude", "Longitude", "Offense_Description", "Street", "Occured_on_Date"]
    dfdirections = dfdirections.dropna(subset=columns)  # Remove rows without valid data
    dfdirections["Latitude"] = pd.to_numeric(dfdirections["Latitude"])
    dfdirections["Longitude"] = pd.to_numeric(dfdirections["Longitude"])
    dfdirections["Latitude"] = dfdirections["Latitude"].astype(float)
    dfdirections["Longitude"] = dfdirections["Longitude"].astype(float)  # Converts coordinates into usable forms
    crime_view = pyd.ViewState(  # Some of this code is adapted from Ivan's presentation in class on maps
        latitude=dfdirections["Latitude"].mean(),  # uses mean latitudes and longitude addresses
        longitude=dfdirections["Longitude"].mean(),
        zoom=11)  # zoom settings for the map
    map_display = st.radio("Choose Map Option", ["All Crimes", "Specific Crimes"])
    if map_display == "All Crimes":
        layer1 = pyd.Layer(  # displays all crimes on the map with basic information
            'ScatterplotLayer',
            data=dfdirections,
            get_position='[Longitude, Latitude]',
            get_radius=25,
            get_color=[255, 0, 0],
            pickable=True)  # Enable pickability for interactivity
        tooltip = {
            "html": "Offense Description:<br/> <b>{Offense_Description}</b> <br/> "
                    "Street: <br/> <b>{Street}</b> <br/> "
                    "Occurred on Date: <br/> <b>{Occured_on_Date}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
        crime_map = pyd.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',  # map style
            initial_view_state=crime_view,
            layers=[layer1],
            tooltip=tooltip
        )
        st.pydeck_chart(crime_map)
    else:
        selected_crimes = st.multiselect(
            "Select Crimes for Display",
            [crime for crime, count in crime_counts.items() if
             (str(count).isdigit() and int(count) > 30) or crime == "MURDER"]
        )
        crime_colors = {}  # make an empty dictionary
        for crime in selected_crimes:  # adds a random color for every specific crime using Numpy
            crime_colors[crime] = (int(np.random.random() * 255), int(np.random.random() * 255),
                                   int(np.random.random() * 255))
        crime_layers = []
        for crime in selected_crimes:
            crime_layer = pyd.Layer(  # adds specific crimes to map rather than adding all of them like earlier
                'ScatterplotLayer',
                data=dfdirections[dfdirections["Offense_Description"] == crime],
                get_position='[Longitude, Latitude]',
                get_radius=30,  # Slightly bigger radius then normal
                get_color=crime_colors[crime],  # puts the random colors generated onto the map
                pickable=True)
            crime_layers.append(crime_layer)
        tooltip = {
            "html": "Offense Description:<br/> <b>{Offense_Description}</b> <br/> "
                    "Street: <br/> <b>{Street}</b> <br/> "
                    "Occurred on Date: <br/> <b>{Occured_on_Date}",
            "style": {"backgroundColor": "steelblue", "color": "white"}}
        crime_map = pyd.Deck(
            map_style='mapbox://styles/mapbox/outdoors-v11',  # map style
            initial_view_state=crime_view,
            layers=[crime_layers],
            tooltip=tooltip)
        st.pydeck_chart(crime_map)


def main():
    dfcrimes = setup()
    crimetimeentertainment(dfcrimes)
    crimemonth_day(dfcrimes)
    dfcrimes, crime_counts = crime_variety(dfcrimes, SLIDER_VALUE)
    crimeplace(dfcrimes, crime_counts)


main()

st.subheader("")
st.write("Works Consulted")
st.caption("https://discuss.streamlit.io/t/how-to-draw-pie-chart-with-matplotlib-pyplot/13967/2")
st.caption("https://stackoverflow.com/questions/76454996/streamlit-streamlit-config-toml")
st.caption("https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_colors.html")
st.caption("https://stackoverflow.com/questions/74866069/trying-to-size-a-legend-issue-in-streamlit")
st.caption("https://www.geeksforgeeks.org/how-to-count-occurrences-of-specific-value-in-pandas-column/")
st.caption("https://www.pythoncharts.com/python/stacked-bar-charts/")
st.caption("https://ggrow3-streamlit-bar-chart-streamlit-app-zbudvw.streamlit.app/")
st.caption("https://blog.finxter.com/bar-charts-learning-streamlit-with-bar-charts/")
st.caption("https://altair-viz.github.io/gallery/stacked_bar_chart.html")
st.caption("https://altair-viz.github.io/user_guide/customization.html#adjusting-axis-labels")
st.caption("https://docs.streamlit.io/library/api-reference/widgets/st.multiselect")
st.caption("https://www.statology.org/matplotlib-random-color/")
st.caption("https://stackoverflow.com/questions/70138089/how-to-order-the-tick-labels-on-a-discrete-axis-0-indexed-"
           "like-a-bar-plot")
