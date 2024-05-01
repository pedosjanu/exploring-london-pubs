
"""
Name: Pedro Ruiz Januario

CS230: Section 6

Data: London Pubs

URL :
Desciption

This interactive web-based application is designed to explore the
fascinating world of London pubs through a detailed and engaging
interface. The core feature of the program is an interactive map that
utilizes geocoding to display the proximity of pubs to the user's
location, providing a visual representation of how close each pub is.
Alongside this, the application offers a comprehensive chart that breaks
down the number of pubs per neighborhood, allowing users to easily
identify areas with the highest concentration of pubs. This feature not
only enhances the user's understanding of the pub distribution across
London but also aids in planning visits based on pub density. To enhance
user interaction, the program includes a dropdown list where users can
search for pubs by name. This functionality is especially useful for
users looking for specific pubs or wanting to explore offerings in
different neighborhoods.
"""
import pandas as pd
import streamlit as st
import pydeck as pdk
import altair as alt

# Cleaning the data
data = pd.read_csv('open_pubs_10000_sample.csv', sep=',', na_values='\\N')
data = data.dropna(subset=['latitude', 'longitude'])

# App title
st.title('Explore London Pubs')

#  Advanced Map Visualization using PyDeck for pub concentrations
st.subheader("Advanced Map Visualization - Pub Concentrations")
view_state = pdk.ViewState(
    latitude=data['latitude'].mean(),
    longitude=data['longitude'].mean(),
    zoom=10,
    pitch=50,
)

hex_layer = pdk.Layer(
    'HexagonLayer',
    data=data,
    get_position='[longitude, latitude]',
    radius=200,
    elevation_scale=4,
    elevation_range=[0, 1000],
    pickable=True,
    extruded=True,
)

# Render the hexagon layer map
r = pdk.Deck(
    layers=[hex_layer],
    initial_view_state=view_state,
    tooltip={'text': 'Concentration of pubs'}
)

st.pydeck_chart(r)

# A function with two or more parameters, one of which has a default value
def load_data(rows=None):
    if rows is None:
        return data
    else:
        return data.sample(rows)

#A list comprehension
pubs = [pub for pub in data['name'].unique()]

# Streamlit widgets for selecting pubs
selected_pubs = st.multiselect('Select pubs to view', pubs, default=pubs[:10])

# Filtering data by one condition - now defining 'filtered_data' correctly
filtered_data = data[data['name'].isin(selected_pubs)]

# Create a bar chart of pubs per neighborhood
st.subheader('Number of Pubs per Neighborhood')
neighborhood_counts = filtered_data['local_authority'].value_counts().reset_index()
neighborhood_counts.columns = ['Neighborhood', 'Count']

#A function that returns a value and is called in at least two different places
def get_plot(data, x, y, title):
    plot = alt.Chart(data).mark_bar().encode(
        x=x,
        y=y,
        tooltip=['Neighborhood', 'Count']
    ).properties(
        title=title
    )
    return plot

plot = get_plot(neighborhood_counts, 'Neighborhood', 'Count', 'Pubs per Neighborhood')
st.altair_chart(plot, use_container_width=True)

# Dropdown to select a pub
selected_pub = st.selectbox('Select a pub', pubs)

# Filtering data by two or more conditions with AND
pub_details = data[(data['name'] == selected_pub) & (data['latitude'].notnull()) & (data['longitude'].notnull())]

# Display details of the selected pub
if not pub_details.empty:
    st.subheader(f'Details for {selected_pub}')
    st.write(pub_details[['address', 'postcode', 'local_authority']])

    # Create a map centered on the selected pub
    view_state = pdk.ViewState(latitude=pub_details['latitude'].iloc[0],
                               longitude=pub_details['longitude'].iloc[0],
                               zoom=15)

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=pub_details,
        get_position='[longitude, latitude]',
        get_radius=100,
        get_fill_color=[255, 0, 0],
        pickable=True
    )

    tool_tip = {'html': 'Name: <br/> <b>{name}</b>'}

    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                   initial_view_state=view_state,
                   layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)
else:
    st.write(f'No details found for {selected_pub}')
