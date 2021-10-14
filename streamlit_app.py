# Import Libs
from datetime import date
import datetime as dt
import io
import base64
from folium.plugins import FastMarkerCluster, HeatMap
import folium
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import streamlit as st
import datetime as dt
import pandas as pd
from dateutil.relativedelta import relativedelta  # to add days or years
import datetime


# read data
df_pararius = pd.read_csv('df_coo_pararius2.csv', index_col=[0])

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
Plaats = st.sidebar.multiselect('Plaats', options=list(
    df_pararius['Plaats'].unique()), default=['Rotterdam'])

# apply filter
df_pararius = df_pararius[df_pararius['Plaats'].isin(Plaats)]

# Filter for price
max_price = int(df_pararius['price'].max())
min_price = int(df_pararius['price'].min())
col1, col2 = st.sidebar.columns(2)
price_selected_0 = col1.number_input(
    'Price (Min)', min_value=0, max_value=max_price, value=0, step=50)
price_selected_1 = col2.number_input(
    'Price (Max)', min_value=0, max_value=max_price, value=1300, step=50)
price_selected = [price_selected_0, price_selected_1]

# Filter for area
max_area = int(df_pararius['surface-area'].max())
min_area = int(df_pararius['surface-area'].min())
area_selected = st.sidebar.slider(
    'Total Area', min_area, max_area, (45, max_area))

validate = st.sidebar.slider('Cost of living', 0, 1000, (0, 500))

####### Date #######
today = date.today()
end_date = today + datetime.timedelta(days=365)
d1 = st.sidebar.date_input("Available", [today, end_date])
d2 = st.sidebar.date_input("Offered since", [today, end_date])

# Filter for interior
my_expander = st.sidebar.expander(label='Advanced Filters')
with my_expander:
    interior_selected = st.multiselect("Interior", options=list(
        df_pararius['interior'].unique()), default=['Furnished'])
    status_selected = st.multiselect("Status", options=list(
        df_pararius['status'].unique()), default=list(df_pararius['status'].unique()))
    max_room = int(df_pararius['number-of-rooms'].max())
    min_room = int(df_pararius['number-of-rooms'].min())
    room_selected = st.slider(
        'number-of-rooms', min_room, max_room, (min_room, max_room))

# organize filter
filter_ = \
    (df_pararius['interior'].isin(interior_selected)) & \
    (df_pararius['status'].isin(status_selected)) & \
    (df_pararius['price'] >= price_selected[0]) & \
    (df_pararius['price'] <= price_selected[1]) & \
    (df_pararius['surface-area'] >= area_selected[0]) & \
    (df_pararius['surface-area'] <= area_selected[1]) & \
    (df_pararius['number-of-rooms'] >= room_selected[0]) & \
    (df_pararius['number-of-rooms'] <= room_selected[1])

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

callback = ('function (row) {'
            "var marker = L.marker(new L.LatLng(row[0], row[1]), {color: 'blue'});"
            "var popup = L.popup({maxWidth: '300'});"
            "const display_text_price = {text: row[2]};"
            "const display_text_link_ = {text: row[3]};"
            "const area = {text: row[4]};"
            "const rooms = {text: row[5]};"
            "const garden = {text: row[6]};"
            "const index = {text: row[7]};"
            "const img = {text: row[8]};"

            "var mytext = $(`\
                            <div id='mytext' class='display_text' style='width: 100.0%; height: 100.0%;'>\
                                <img src=${img.text} title='house' width='150' height='100'/>\
                                <br>\
                                Index - ${index.text}<br>\
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
area = good['surface-area'].tolist()
rooms = good['number-of-rooms'].tolist()
garden = good['garden-surface-area'].tolist()
index = good.index.tolist()
image = good['image'].tolist()

locations = list(zip(lats, lons, price, irl, area,
                 rooms, garden, index, image))

# MAP
OP = [51.9071833, 4.4728155]
pararius = folium.Map(OP, tiles="cartodbdark_matter")
# add zoom
sw = good[['latitude', 'longitude']].min().values.tolist()
ne = good[['latitude', 'longitude']].max().values.tolist()
pararius.fit_bounds([sw, ne])
# add data to map
FastMarkerCluster(data=locations, name='good', callback=callback,
                  show=True, tooltip='tooltip').add_to(pararius)
# HeatMap(good[['latitude', 'longitude', 'deal']].values.tolist(),name='good HeatMap', show=False).add_to(pararius)
icon_url = 'https://media-exp1.licdn.com/dms/image/C4D0BAQHSDPW5wBr9eA/company-logo_200_200/0/1623138109412?e=2159024400&v=beta&t=XM6Umkb8JZ6XNliPWZzaNxjLgkL8BCv8newgm3VvTx8'
icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
folium.Marker(location=OP, icon=icon).add_to(pararius)
folium.LayerControl().add_to(pararius)

# plot map on streamlit
st.write(pararius)

# plot data on streamlit
good_ = good[[
    'img',
    'price',
    'Plaats',
    'surface-area',
    'number-of-rooms',
    'garden-surface-area',
    'Offered since',
    'Available',
]].rename(columns={
    'img': 'Add',
    'price': 'Price',
    'Plaats': 'City',
    'surface-area': 'Area',
    'number-of-rooms': 'Rooms',
    'garden-surface-area': 'Garden',
    'Offered since': 'Offered',
    'Available': 'Available',
}).to_html(escape=False)

# good_ = good[['img', 'price', 'link', 'agency', 'surface-area', 'number-of-rooms','garden-surface-area', 'Offered since', 'Available']].to_html(escape=False)
# prepare to download
# towrite = io.BytesIO()
# downloaded_file = good[["url", "price", "address", "street", "agency", "date"]].to_excel(
#     towrite, encoding='utf-8', index=False, header=True)
# towrite.seek(0)  # reset pointer
# b64 = base64.b64encode(towrite.read()).decode()  # some strings
# linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="rents_denhaag.xlsx">Download excel file</a>'
# st.text(" \n")
#st.markdown(linko, unsafe_allow_html=True)

st.text(" \n")
st.write(good_, unsafe_allow_html=True)
