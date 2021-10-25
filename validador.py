from st_aggrid import AgGrid, GridOptionsBuilder, shared
import seaborn as sns
import folium
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
# https://github.com/PablocFonseca/streamlit-aggrid/blob/main/st_aggrid/grid_options_builder.py
st.set_page_config(layout='wide')
st.title('Costs of Living')
st.markdown("Selecting multiple rows can be achieved by holding down Ctrl and mouse clicking the rows. A range of rows can be selected by using Shift.")

final = pd.read_csv('costs.csv')

row1, row2 = st.columns(2)

max_distance = int(final['distance'].max())
min_distance = int(final['distance'].min())
distance_selected = row1.slider(
    'Total distance', min_distance, max_distance, (min_distance, max_distance))
max_price = int(final['price'].max())
min_price = int(final['price'].min())
price_selected = row2.slider(
    'Total price', min_price, max_price, (min_price, max_price))


filter_ = (final['distance'] >= distance_selected[0]) & (final['distance'] <= distance_selected[1]) & (
    final['price'] >= price_selected[0]) & (final['price'] <= price_selected[1])
final = final[filter_]

lats = final['latitude'].tolist()
lons = final['longitude'].tolist()
city = final['city'].tolist()
price = final['price'].tolist()
map = folium.Map(location=[52.2129919, 5.2793703],
                 zoom_start=7, tiles="cartodbdark_matter")
color_pallete = (sns.color_palette("viridis", len(price))).as_hex()
feature_group = folium.FeatureGroup("Locations")
i = 0
for lats, lons, price, city in zip(lats, lons, price, city):
    feature_group.add_child(folium.CircleMarker(
        location=[lats, lons],
        popup=f"{city}, €{price}",
        radius=4,
        color=color_pallete[i],
        fill=True,
        fill_opacity=1))
    i += 1
icon_url = 'https://media-exp1.licdn.com/dms/image/C4D0BAQHSDPW5wBr9eA/company-logo_200_200/0/1623138109412?e=2159024400&v=beta&t=XM6Umkb8JZ6XNliPWZzaNxjLgkL8BCv8newgm3VvTx8'
icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
folium.Marker(location=[51.9071833, 4.4728155],
              icon=icon, popup='Obvious People').add_to(map)
map.add_child(feature_group)


def display_table(df: pd.DataFrame) -> AgGrid:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_default_column(min_column_width=10, resizable=True,
                                filterable=True, sorteable=True, editable=True, groupable=True,)
    return AgGrid(df, gridOptions=gb.build(), update_mode=shared.GridUpdateMode.MODEL_CHANGED)


st.session_state.display_table = True
t = display_table(final[['price', 'city', 'distance', 'address']])
st.write(map)

amount = len(t["selected_rows"])
ault = []
for i in range(amount):
    ault.append(t["selected_rows"][i]["city"])

if 'page' not in st.session_state:
    st.session_state.update({
        'page': 'Home',
        "options": final['city'].unique(),
        "multiselect": ault,
    })
st.multiselect("Multiselect", key=ault)
st.session_state.multiselect
# st.json(t["selected_rows"])
# import SessionState
# st.session_state.get(name="", button_sent=False)
