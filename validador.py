# Import Libs
from folium.plugins import FastMarkerCluster
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
import base64
import folium
import io
import pandas as pd
import seaborn as sns
import streamlit as st


def main():
    # create streamlit page
    st.set_page_config(layout='wide')

    # config streamlit layout
    hide_streamlit_style = """
    <style>
    # MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .css-1y0tads {padding-top: 0rem;}
    .css-hby737 {padding: 1rem 1rem;}
    .css-ijjfg8 {width: 25px;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # pages = {'Costs of Living': page_settings}
    # page = st.sidebar.radio('Select your page', tuple(pages.keys()))
    # pages[page]()
    page_settings()


def page_settings():
    st.title('Costs of Living')

    @st.cache
    def fetch_and_clean_data1():
        df = pd.read_csv('costs.csv')
        return df
    final = fetch_and_clean_data1()

    def display_table(df: pd.DataFrame) -> AgGrid:
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True,
                                    aggFunc='sum', editable=True, groupSelectsChildren=True, groupSelectsFiltered=True)
        gb.configure_selection('multiple', use_checkbox=True)
        gb.configure_pagination(enabled=True)
        gridOptions = gb.build()
        main_grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            height=400,
            width='100%',
            update_mode=GridUpdateMode.MODEL_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
        )
        return main_grid_response

    # positioning
    row1, row2 = st.columns(2)

    # distance selected slider
    max_distance = int(final['distance'].max())
    min_distance = int(final['distance'].min())
    distance_selected = st.sidebar.slider(
        'Total distance', min_distance, max_distance, (min_distance, max_distance))

    # price selected slider
    max_price = int(final['price'].max())
    min_price = int(final['price'].min())
    price_selected = st.sidebar.slider(
        'Total price', min_price, max_price, (min_price, max_price))

    # filter
    filter_ = (final['distance'] >= distance_selected[0]) & (final['distance'] <= distance_selected[1]) & (
        final['price'] >= price_selected[0]) & (final['price'] <= price_selected[1])

    # add filter
    final = final[filter_]

    # table
    st.session_state.display_table = True
    t = display_table(final)

    ault = []
    amount = len(t["selected_rows"])
    for i in range(amount):
        ault.append(t["selected_rows"][i]["city"])

    if len(ault) > 0:
        final = final[final['city'].isin(ault)]
    else:
        pass
    final = final.sort_values('price')
    lats = final['latitude'].tolist()
    lons = final['longitude'].tolist()
    city = final['city'].tolist()
    price = final['price'].tolist()

    map = folium.Map(location=[52.2129919, 5.2793703], zoom_start=7)
    color_pallete = (sns.color_palette("YlOrBr", len(price))).as_hex()
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
    map.add_child(feature_group)
    row1.write(map)

    st.title("Places to rent in The Netherlands")

    @st.cache
    # read data
    def fetch_and_clean_data2():
        df = pd.read_csv('df_coo_pararius2.csv', index_col=[0])
        return df
    df_pararius = fetch_and_clean_data2()

    # create filter for city
    if len(ault) > 0:
        default_val = ault

    else:
        default_val = ["Rotterdam"]

    df_pararius = df_pararius[df_pararius['City'].isin(default_val)]

    # Filter for price
    max_price = int(df_pararius['Price'].max())
    min_price = int(df_pararius['Price'].min())
    col1, col2 = st.sidebar.columns(2)
    price_selected_0 = col1.number_input(
        'Price (Min)', min_value=0, max_value=max_price, value=0, step=50)
    price_selected_1 = col2.number_input(
        'Price (Max)', min_value=0, max_value=max_price, value=1300, step=50)
    price_selected = [price_selected_0, price_selected_1]

    # Filter for area
    max_area = int(df_pararius['Area'].max())
    min_area = int(df_pararius['Area'].min())
    area_selected = st.sidebar.slider(
        'Total Area', min_area, max_area, (45, max_area))

    # Filter for interior
    my_expander = st.sidebar.expander(label='Advanced Filters')
    with my_expander:
        # Filter for Date
        df_pararius['Offered'] = pd.to_datetime(
            df_pararius['Offered'], format='%d-%m-%Y')
        max_offered = (df_pararius['Offered'].max())
        min_offered = (df_pararius['Offered'].min())
        d1 = st.date_input('Offered since', [min_offered, max_offered])
        min_offered = (pd.to_datetime(d1[0], format='%Y-%m-%d'))
        max_offered = (pd.to_datetime(d1[1], format='%Y-%m-%d'))

        # Filter for Date
        df_pararius['Available'] = pd.to_datetime(
            df_pararius['Available'], format='%d-%m-%Y')
        max_available = (df_pararius['Available'].max())
        min_available = (df_pararius['Available'].min())
        d2 = st.date_input('Available', [min_available, max_available])
        min_available = (pd.to_datetime(d2[0], format='%Y-%m-%d'))
        max_available = (pd.to_datetime(d2[1], format='%Y-%m-%d'))

        interior_selected = st.multiselect('Interior', options=list(
            df_pararius['interior'].unique()), default=list(df_pararius['interior'].unique()))

        status_selected = st.multiselect('Status', options=list(
            df_pararius['status'].unique()), default=list(df_pararius['status'].unique()))

        max_room = int(df_pararius['Rooms'].max())
        min_room = int(df_pararius['Rooms'].min())
        room_selected = st.slider(
            'Rooms', min_room, max_room, (min_room, max_room))

    # organize filter
    filter_ = \
        (df_pararius['interior'].isin(interior_selected))\
        & (df_pararius['status'].isin(status_selected))\
        & (df_pararius['Price'] >= price_selected[0])\
        & (df_pararius['Price'] <= price_selected[1])\
        & (df_pararius['Area'] >= area_selected[0])\
        & (df_pararius['Area'] <= area_selected[1])\
        & (df_pararius['Rooms'] >= room_selected[0])\
        & (df_pararius['Rooms'] <= room_selected[1])\
        & (df_pararius['Offered'] >= min_offered)\
        & (df_pararius['Offered'] <= max_offered)\
        & (df_pararius['Available'] >= min_available)\
        & (df_pararius['Available'] <= max_available)\

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
    good = df_pararius[(df_pararius.index >= index_selected[0]) & (
        df_pararius.index <= index_selected[1])]

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
    price = good['Price'].tolist()
    irl = good['irl'].tolist()
    area = good['Area'].tolist()
    rooms = good['Rooms'].tolist()
    garden = good['Garden'].tolist()
    index = good.index.tolist()
    image = good['image'].tolist()

    locations = list(zip(lats, lons, price, irl, area,
                     rooms, garden, index, image))

    # MAP
    OP = [51.9071833, 4.4728155]
    pararius = folium.Map(OP, tiles='cartodbdark_matter')

    # add zoom
    sw = good[['latitude', 'longitude']].min().values.tolist()
    ne = good[['latitude', 'longitude']].max().values.tolist()
    pararius.fit_bounds([sw, ne])

    # add data to map
    FastMarkerCluster(data=locations, name='good', callback=callback,
                      show=True, tooltip='tooltip').add_to(pararius)

    icon_url = 'https://media-exp1.licdn.com/dms/image/C4D0BAQHSDPW5wBr9eA/company-logo_200_200/0/1623138109412?e=2159024400&v=beta&t=XM6Umkb8JZ6XNliPWZzaNxjLgkL8BCv8newgm3VvTx8'
    icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
    folium.Marker(location=OP, icon=icon).add_to(pararius)
    folium.LayerControl().add_to(pararius)

    # plot map on streamlit
    st.write(pararius)

    # plot data on streamlit
    good_ = good[[
        'Add',
        'Price',
        'City',
        'Area',
        'Rooms',
        'Garden',
        'Offered',
        'Available',
    ]].to_html(escape=False)

    # prepare to download
    towrite = io.BytesIO()
    good[['url', 'Price', 'address', 'street', 'agency', 'date']].to_excel(
        towrite, encoding='utf-8', index=False, header=True)
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()  # some strings
    linko = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="obvious_people_houses.xlsx">Download excel file</a>'
    st.text(" \n")
    st.markdown(linko, unsafe_allow_html=True)
    st.text(" \n")
    st.write(good_, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
