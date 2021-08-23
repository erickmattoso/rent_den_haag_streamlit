# Import Libs
import io
import base64
from folium.plugins import FastMarkerCluster, HeatMap
import folium
import pandas as pd
import streamlit as st

# read data
# df_pararius
df_pararius = pd.read_csv('df_coo_pararius.csv', index_col=[0])

# yelp
#yelp = pd.read_csv('yelp.csv', index_col=[0])

# create streamlit page
st.set_page_config(layout="wide")
# config streamlit layout
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.css-1y0tads {padding-top: 0rem;}
.css-hby737 {padding: 1rem 1rem;}
.css-ijjfg8 {width: 25px;}
</style
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title("Places to rent in The Netherlands")

# create filter on sidebar
city = st.sidebar.multiselect("City", options=list(
    df_pararius['city'].unique()), default=['Den Haag'])

# apply filter
df_pararius = df_pararius[df_pararius['city'].isin(city)]

# Filter for price
max_price = int(df_pararius['price'].max())
min_price = int(df_pararius['price'].min())
col1, col2 = st.sidebar.columns(2)
price_selected_0 = col1.number_input(
    'Price (Min)', min_value=0, max_value=max_price, value=0)
price_selected_1 = col2.number_input(
    'Price (Max)', min_value=0, max_value=max_price, value=1100)
price_selected = [price_selected_0, price_selected_1]

# Filter for area
max_area = int(df_pararius['Living area'].max())
min_area = int(df_pararius['Living area'].min())
area_selected = st.sidebar.slider(
    'Total Area', min_area, max_area, (45, max_area))

# Filter for interior
my_expander = st.sidebar.expander(label='Advanced Filters')
with my_expander:
    interior_selected = st.multiselect("Interior", options=list(
        df_pararius['interior'].unique()), default=['Furnished'])
    status_selected = st.multiselect("Status", options=list(
        df_pararius['status'].unique()), default=list(df_pararius['status'].unique()))
    max_room = int(df_pararius['Rooms'].max())
    min_room = int(df_pararius['Rooms'].min())
    room_selected = st.slider(
        'Rooms', min_room, max_room, (min_room, max_room))

# organize filter
filter_ = \
    (df_pararius['interior'].isin(interior_selected)) & \
    (df_pararius['status'].isin(status_selected)) & \
    (df_pararius['price'] >= price_selected[0]) & \
    (df_pararius['price'] <= price_selected[1]) & \
    (df_pararius['Living area'] >= area_selected[0]) & \
    (df_pararius['Living area'] <= area_selected[1]) & \
    (df_pararius['Rooms'] >= room_selected[0]) & \
    (df_pararius['Rooms'] <= room_selected[1])


# apply filter
df_pararius = df_pararius[filter_]

# define order of best deal
df_pararius = df_pararius.sort_values(
    'deal', ascending=False).reset_index(drop=True)

# Here I will tell how many I want to check
max_val = int(df_pararius.index.max())
min_val = int(df_pararius.index.min())
index_selected = st.sidebar.slider(
    'Amout houses', min_val, max_val, (min_val, 10))

# apply filter
good = df_pararius[(df_pararius.index >= index_selected[0])
                   & (df_pararius.index <= index_selected[1])]

# MAP
pararius = folium.Map([52.0799838, 4.3113461],
                      zoom_start=12, tiles="cartodbdark_matter")

# add data to map
#FastMarkerCluster(data=locations, name='good', callback=callback,show=True, tooltip='tooltip').add_to(pararius)

callback = ('function (row) {'
            "var marker = L.marker(new L.LatLng(row[0], row[1]), {color: 'blue'});"
            "var popup = L.popup({maxWidth: '300'});"
            "const display_text_price = {text: row[2]};"
            "const display_text_link_ = {text: row[3]};"
            "const area = {text: row[4]};"
            "const rooms = {text: row[5]};"
            "const garden = {text: row[6]};"
            "const index_ = {text: row[7]};"
            "var mytext = $(`\
                            <div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'>\
                                <img src='https://www.publicdomainpictures.net/pictures/320000/velka/background-image.png' title='titulo' width='200' height='100'/>\
                                <br>\
                                Index - ${index_.text}<br>\
                                Price - € ${display_text_price.text}<br>\
                                Area - ${area.text} m² <br>\
                                Rooms - ${rooms.text}<br>\
                                Garden - ${garden.text} m² <br>\
                                <a href=https://www.pararius.com${display_text_link_.text} target='blank'> Source </a>\
                            </div>`)[0];"
            "popup.setContent(mytext);"
            "marker.bindPopup(popup);"
            'return marker};')
# prepare data to map
lats = good['latitude'].tolist()
lons = good['longitude'].tolist()
deal = good['deal'].tolist()
price = good['price'].tolist()
irl = good['irl'].tolist()
area = good['Living area'].tolist()
rooms = good['Rooms'].tolist()
garden = good['garden area'].tolist()
index = good['garden area'].index.tolist()
locations = list(zip(lats, lons, price, irl, area, rooms, garden, index))

# add data to map
FastMarkerCluster(data=locations, name='good', callback=callback,
                  show=True, tooltip='tooltip').add_to(pararius)
HeatMap(good[['latitude', 'longitude', 'deal']].values.tolist(),
        name='good HeatMap', show=False).add_to(pararius)
folium.LayerControl().add_to(pararius)

# plot map on streamlit
st.write(pararius)

# plot data on streamlit
good_ = good[['price', 'link', 'agency', 'Living area',
              'Rooms', 'garden area']].to_html(escape=False)

# prepare to download
towrite = io.BytesIO()
downloaded_file = good[["url", "price", "address", "street", "agency", "date"]].to_excel(
    towrite, encoding='utf-8', index=False, header=True)
towrite.seek(0)  # reset pointer
b64 = base64.b64encode(towrite.read()).decode()  # some strings
linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="rents_denhaag.xlsx">Download excel file</a>'
st.text(" \n")
st.markdown(linko, unsafe_allow_html=True)
st.text(" \n")
st.write(good_, unsafe_allow_html=True)
