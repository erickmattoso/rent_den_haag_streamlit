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
    col1, col2, col3 = st.columns([0.2, 0.70, 0.2])
    with col1:
        st.image(Image.open('obviouspeople_.png'), width=225)
    # with col2:
    #     st.markdown(
    #         """<style>.font{color:green;font-size:18px;padding-left:50px;text-decoration:none;font-weight: bold;}</style>""", unsafe_allow_html=True)
    #     st.markdown(
    #         """
    #             <a href='/solutions'            class='font'>Solutions</a>
    #             <a href='/salesforce-academy'   class='font'>Academy</a>
    #             <a href='/community'            class='font'>Community</a>
    #             <a href='/services'             class='font'>Services</a>
    #             <a href='/about-us'             class='font'>About</a>
    #         """,
    #         unsafe_allow_html=True)
    # with col3:
    #     url = 'https://www.streamlit.io/'
    #     if st.button('Open browser'):
    #         webbrowser.open_new_tab(url)

    # Lorem
    st.title('Costs of Living')

    # Lorem
    original = pd.read_csv('df_housing_app.csv', index_col=[0])

    final = original.copy()

    # Lorem
    def display_table(df: pd.DataFrame) -> AgGrid:
        df = df[[
            'city',
            'province',
            'alternate names',
            'population',
            'cost',
            'distance',
            'distance']]

        df = df.drop_duplicates('city')
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
    distance_selected = row2.slider(
        'Distance from Obvious People', min_distance, max_distance, (min_distance, max_distance))

    # cost selected slider
    max_cost = int(final['cost'].max()+1)
    min_cost = int(final['cost'].min()-1)
    cost_selected = row2.slider(
        'Cost of Living', min_cost, max_cost, (min_cost, max_cost))

    # filter
    filter_ = (final['distance'] >= distance_selected[0]) & (final['distance'] <= distance_selected[1]) & (
        final['cost'] >= cost_selected[0]) & (final['cost'] <= cost_selected[1])

    # add filter

    final = final[filter_]
    # st.write(final[final['cost'].isna()])

    # table
    st.session_state.display_table = True
    t = display_table(final.drop(columns=['latitude_city', 'longitude_city']))
    # Lorem
    ault = []
    amount = len(t["selected_rows"])
    for i in range(amount):
        ault.append(t["selected_rows"][i]["city"])

    # Lorem
    if len(ault) > 0:
        final = final[final['city'].isin(ault)]
        default_val = ault
    else:
        default_val = list(final['city'].unique())
        pass

    # Lorem
    final = final.sort_values('cost')
    lats = final['latitude_city'].tolist()
    lons = final['longitude_city'].tolist()
    city = final['city'].tolist()
    cost = final['cost'].tolist()

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
    sw = final[['latitude_city', 'longitude_city']].min().values.tolist()
    ne = final[['latitude_city', 'longitude_city']].max().values.tolist()
    map.fit_bounds([sw, ne])
    row1.write(map)

    # Lorem
    st.title("Places to rent in The Netherlands")

    # Lorem
    # read data
    def fetch_and_clean_data2():
        df = original.copy()
        return df
    df_pararius = fetch_and_clean_data2()

    # read data
    df_pararius = df_pararius[df_pararius['city'].isin(default_val)]

    # Filter for price
    max_price = (df_pararius['price'].max())
    min_price = (df_pararius['price'].min())

    # Lorem
    row1, row2 = st.columns(2)

    # Lorem
    price_selected_0 = row2.number_input(
        'price (Min)', min_value=0, max_value=max_price, value=0, step=50)
    price_selected_1 = row2.number_input(
        'price (Max)', min_value=0, max_value=max_price, value=max_price, step=50)
    price_selected = [price_selected_0, price_selected_1]

    # Filter for area
    max_area = int(df_pararius['dimensions living area'].max())
    min_area = int(df_pararius['dimensions living area'].min())
    area_selected = row2.slider(
        'Total Area', min_area, max_area, (0, max_area))

    # Filter for interior
    my_expander = row2.expander(label='Advanced Filters')

    # Filter for Date
    with my_expander:
        df_pararius["transfer offered since"] = pd.to_datetime(
            df_pararius["transfer offered since"], format='%d-%m-%Y')
        max_offered = (df_pararius["transfer offered since"].max())
        min_offered = (df_pararius["transfer offered since"].min())
        d1 = st.date_input('Offered since', [min_offered, max_offered])
        min_offered = (pd.to_datetime(d1[0], format='%Y-%m-%d'))
        max_offered = (pd.to_datetime(d1[1], format='%Y-%m-%d'))

        # Filter for Date
        df_pararius['transfer available'] = pd.to_datetime(
            df_pararius['transfer available'], format='%d-%m-%Y')
        max_available = (df_pararius['transfer available'].max())
        min_available = (df_pararius['transfer available'].min())
        d2 = st.date_input('transfer available', [
                           min_available, max_available])
        min_available = (pd.to_datetime(d2[0], format='%Y-%m-%d'))
        max_available = (pd.to_datetime(d2[1], format='%Y-%m-%d'))

        # Filter for Date
        interior_selected = st.multiselect('transfer interior', options=list(
            df_pararius['transfer interior'].unique()), default=list(df_pararius['transfer interior'].unique()))
        status_selected = st.multiselect('transfer status', options=list(
            df_pararius['transfer status'].unique()), default=list(df_pararius['transfer status'].unique()))

        # Filter for Date
        max_room = int(df_pararius['layout number of rooms'].max())
        min_room = int(df_pararius['layout number of rooms'].min())
        room_selected = st.slider(
            'layout number of rooms', min_room, max_room, (min_room, max_room))

    # organize filter
    filter_ = \
        (df_pararius['transfer interior'].isin(interior_selected))\
        & (df_pararius['transfer status'].isin(status_selected))\
        & (df_pararius['price'] >= price_selected[0])\
        & (df_pararius['price'] <= price_selected[1])\
        & (df_pararius['dimensions living area'] >= area_selected[0])\
        & (df_pararius['dimensions living area'] <= area_selected[1])\
        & (df_pararius['layout number of rooms'] >= room_selected[0])\
        & (df_pararius['layout number of rooms'] <= room_selected[1])\
        & (df_pararius["transfer offered since"] >= min_offered)\
        & (df_pararius["transfer offered since"] <= max_offered)\
        & (df_pararius['transfer available'] >= min_available)\
        & (df_pararius['transfer available'] <= max_available)\

    # apply filter
    df_pararius = df_pararius[filter_]

    # define order of best deal
    df_pararius = df_pararius.sort_values(
        'deal', ascending=False).reset_index(drop=True)

    # Here I will tell how many I want to check
    max_val = int(df_pararius.index.max())
    min_val = int(df_pararius.index.min())
    index_selected = row2.slider(
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
    icon_url = 'https://media-exp1.licdn.com/dms/image/C4D0BAQHSDPW5wBr9eA/company-logo_200_200/0/1623138109412?e=2159024400&v=beta&t=XM6Umkb8JZ6XNliPWZzaNxjLgkL8BCv8newgm3VvTx8'
    icon = folium.features.CustomIcon(icon_url, icon_size=(28, 30))
    folium.Marker(location=OP, icon=icon).add_to(pararius)
    folium.LayerControl().add_to(pararius)

    # plot map on streamlit
    row1.write(pararius)

    # plot data on streamlit
    good_ = good[[
        'image',
        'title',
        'price',
        'city',
        'dimensions living area',
        'layout number of rooms',
        'outdoor garden',
        "transfer offered since",
        'transfer available',
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
