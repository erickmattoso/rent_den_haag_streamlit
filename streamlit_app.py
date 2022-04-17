# Import Libs
from folium.plugins import FastMarkerCluster
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
import base64
import folium
import io
import pandas as pd
import seaborn as sns
import streamlit as st
from PIL import Image, ImageEnhance


def main():
    # create streamlit page
    st.set_page_config(
        layout='wide', page_title='ObviousPeopleApp', page_icon="🏠")

    # config streamlit layout
    hide_streamlit_style = """
    <style>
    .css-18e3th9 {padding: 1rem 5rem 10rem;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    page_settings()


def page_settings():
    # icon
    st.markdown('''<a href="https://obviouspeople.webflow.io"><img src="https://raw.githubusercontent.com/erickmattoso/rent_den_haag_streamlit/main/obviouspeople_.png" width='225'/></a>''', unsafe_allow_html=True)

    # title
    st.title('Costs of Living')

    # read files
    df_housing = pd.read_csv('df_housing_app.csv', index_col=[0])[
        ['price', 'city', 'dimensions living area', 'transfer offered since', 'transfer available', 'transfer interior', 'transfer status', 'layout number of rooms', 'deal', 'latitude', 'longitude', 'url', 'img', 'outdoor garden', 'image']]

    cost_liv = pd.read_csv('cost_living.csv', index_col=[0])

    # Lorem
    def display_table(df: pd.DataFrame) -> AgGrid:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True,
                                    aggFunc='sum', editable=True, groupSelectsChildren=True, groupSelectsFiltered=True)
        gb.configure_selection('multiple', use_checkbox=True)
        gb.configure_pagination(enabled=True)
        gridOptions = gb.build()
        main_grid_response = AgGrid(df, gridOptions=gridOptions, height=400,
                                    update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True, fit_columns_on_grid_load=True)
        return main_grid_response

    # positioning
    row1, row2 = st.columns(2)

    # distance selected slider
    max_distance = int(cost_liv['distance'].max())
    min_distance = int(cost_liv['distance'].min())
    distance_selected = row2.slider(
        'Distance from Obvious People', min_distance, max_distance, (min_distance, max_distance))

    # cost selected slider
    max_cost = int(cost_liv['cost'].max()+1)
    min_cost = int(cost_liv['cost'].min()-1)
    cost_selected = row2.slider(
        'Cost of Living', min_cost, max_cost, (min_cost, max_cost))

    # filter
    filter_ = (cost_liv['distance'] >= distance_selected[0]) & (cost_liv['distance'] <= distance_selected[1]) & (
        cost_liv['cost'] >= cost_selected[0]) & (cost_liv['cost'] <= cost_selected[1])

    # add filter
    cost_liv = cost_liv[filter_]

    # table
    st.session_state.display_table = True
    t = display_table(cost_liv.drop(
        columns=['distance', 'latitude_city', 'longitude_city']))

    # Lorem
    ault = []
    amount = len(t["selected_rows"])
    for i in range(amount):
        ault.append(t["selected_rows"][i]["city"])

    # Lorem
    if len(ault) > 0:
        cost_liv = cost_liv[cost_liv['city'].isin(ault)]
        default_val = ault
    else:
        default_val = list(cost_liv['city'].unique())
        pass

    # Lorem
    # cost_liv = cost_liv.sort_values('deal', ascending=False).reset_index(drop=True)
    lats = cost_liv['latitude_city'].tolist()
    lons = cost_liv['longitude_city'].tolist()
    city = cost_liv['city'].tolist()
    cost = cost_liv['cost'].tolist()

    # Lorem
    OP = [51.9071833, 4.4728155]
    map = folium.Map(OP, tiles='cartodbdark_matter')
    color_pallete = (sns.color_palette("YlOrBr", len(cost))).as_hex()
    feature_group = folium.FeatureGroup("Locations")

    # Lorem
    i = 0
    for lats, lons, cost, city in zip(lats, lons, cost, city):
        feature_group.add_child(folium.CircleMarker(
            location=[lats, lons],
            popup=f"{city}, €{cost}",
            radius=4,
            color=color_pallete[i],
            fill=True,
            fill_opacity=1))
        i += 1

    # Lorem
    map.add_child(feature_group)

    # add zoom
    sw = cost_liv[['latitude_city', 'longitude_city']].min().values.tolist()
    ne = cost_liv[['latitude_city', 'longitude_city']].max().values.tolist()
    map.fit_bounds([sw, ne])
    row1.write(map)

    # Lorem 2
    st.title("Places to rent in The Netherlands")

    # read data
    df_housing = df_housing[df_housing['city'].isin(default_val)]

    # Filter for price
    max_price = (df_housing['price'].max())
    min_price = (df_housing['price'].min())

    # Lorem
    row1, row2 = st.columns(2)

    # Filter for area
    max_price = int(df_housing['price'].max())
    min_price = int(df_housing['price'].min())
    price_selected = row2.slider(
        'Price', min_price, max_price, (min_price, max_price))

    # Filter for area
    max_area = int(df_housing['dimensions living area'].max())
    min_area = int(df_housing['dimensions living area'].min())
    area_selected = row2.slider(
        'Total Area', min_area, max_area, (0, max_area))

    # Filter for interior
    my_expander = row2.expander(label='Advanced Filters')

    # Filter for Date
    with my_expander:
        df_housing["transfer offered since"] = pd.to_datetime(
            df_housing["transfer offered since"], format='%d-%m-%Y')
        max_offered = (df_housing["transfer offered since"].max())
        min_offered = (df_housing["transfer offered since"].min())
        d1 = st.date_input('Offered since', [min_offered, max_offered])
        min_offered = (pd.to_datetime(d1[0], format='%Y-%m-%d'))
        max_offered = (pd.to_datetime(d1[1], format='%Y-%m-%d'))

        # Filter for Date
        df_housing['transfer available'] = pd.to_datetime(
            df_housing['transfer available'], format='%d-%m-%Y')
        max_available = (df_housing['transfer available'].max())
        min_available = (df_housing['transfer available'].min())
        d2 = st.date_input('transfer available', [
            min_available, max_available])
        min_available = (pd.to_datetime(d2[0], format='%Y-%m-%d'))
        max_available = (pd.to_datetime(d2[1], format='%Y-%m-%d'))

        # Filter for Date
        interior_selected = st.multiselect('transfer interior', options=list(
            df_housing['transfer interior'].unique()), default=list(df_housing['transfer interior'].unique()))
        status_selected = st.multiselect('transfer status', options=list(
            df_housing['transfer status'].unique()), default=list(df_housing['transfer status'].unique()))

        # Filter for Date
        max_room = int(df_housing['layout number of rooms'].max())
        min_room = int(df_housing['layout number of rooms'].min())
        room_selected = st.slider(
            'layout number of rooms', min_room, max_room, (min_room, max_room))

    # organize filter
    filter_ = (df_housing['transfer interior'].isin(interior_selected))\
        & (df_housing['transfer status'].isin(status_selected))\
        & (df_housing['price'] >= price_selected[0])\
        & (df_housing['price'] <= price_selected[1])\
        & (df_housing['dimensions living area'] >= area_selected[0])\
        & (df_housing['dimensions living area'] <= area_selected[1])\
        & (df_housing['layout number of rooms'] >= room_selected[0])\
        & (df_housing['layout number of rooms'] <= room_selected[1])\
        & (df_housing["transfer offered since"] >= min_offered)\
        & (df_housing["transfer offered since"] <= max_offered)\
        & (df_housing['transfer available'] >= min_available)\
        & (df_housing['transfer available'] <= max_available)\

    # apply filter
    df_housing = df_housing[filter_]

    # define order of best deal
    df_housing = df_housing.sort_values(
        'deal', ascending=False).reset_index(drop=True)

    # Here I will tell how many I want to check
    max_val = int(df_housing.index.max())
    min_val = int(df_housing.index.min())
    index_selected = row2.slider(
        'Amout houses', min_val, max_val, (min_val, 10))

    # apply filter
    good = df_housing[(df_housing.index >= index_selected[0]) & (
        df_housing.index <= index_selected[1])]

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
                                    price - € ${display_text_price.text}<br>\
                                    Area - ${area.text} m² <br>\
                                    Rooms - ${rooms.text}<br>\
                                    Garden - ${garden.text} m² <br>\
                                    <a href=${display_text_link_.text} target='blank'> Source </a>\
                                </div>`)[0];"
                "popup.setContent(mytext);"
                "marker.bindPopup(popup);"
                'return marker};')

    # prepare data to map
    lats = good['latitude'].tolist()
    lons = good['longitude'].tolist()
    price = good['price'].tolist()
    irl = good['url'].tolist()
    area = good['dimensions living area'].tolist()
    rooms = good['layout number of rooms'].tolist()
    garden = good['outdoor garden'].tolist()
    index = good.index.tolist()
    image = good['img'].tolist()

    # Lorem
    locations = list(zip(lats, lons, price, irl, area,
                         rooms, garden, index, image))

    # MAP
    pararius = folium.Map(OP, tiles='cartodbdark_matter')

    # add zoom
    sw = good[['latitude', 'longitude']].min().values.tolist()
    ne = good[['latitude', 'longitude']].max().values.tolist()
    pararius.fit_bounds([sw, ne])

    # add data to map
    FastMarkerCluster(data=locations, name='good', callback=callback,
                      show=True, tooltip='tooltip').add_to(pararius)
    icon_url = 'https://raw.githubusercontent.com/erickmattoso/rent_den_haag_streamlit/main/obviouspeople.png'
    icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
    folium.Marker(location=OP, icon=icon).add_to(pararius)
    folium.LayerControl().add_to(pararius)

    # plot map on streamlit
    row1.write(pararius)

    # plot data on streamlit
    good_ = good[[
        'image',
        'price',
        'city',
        'dimensions living area',
        'layout number of rooms',
        'outdoor garden',
        "transfer offered since",
        'transfer available'
    ]].to_html(escape=False)

    # prepare to download
    towrite = io.BytesIO()
    good.to_excel(towrite, encoding='utf-8', index=False, header=True)

    # reset pointer
    towrite.seek(0)

    # some strings
    b64 = base64.b64encode(towrite.read()).decode()
    linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="obvious_people_houses.xlsx">Download excel file</a>'
    st.text(" \n")
    st.markdown(linko, unsafe_allow_html=True)
    st.text(" \n")
    st.write(good_, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
