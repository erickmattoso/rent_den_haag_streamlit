import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache()
def load_data():
    df = pd.read_csv(
        'https://github.com/chris1610/pbpython/blob/master/data/cereal_data.csv?raw=True'
    )
    return df


# Read in the cereal data
df = load_data()

st.title('Rating exploration')

# Only a subset of options make sense
x_options = [
    'calories', 'protein', 'fat', 'sodium', 'fiber', 'carbo', 'sugars',
    'potass'
]

# Allow use to choose
x_axis = st.sidebar.selectbox('Which value do you want to explore?', x_options)

# plot the value
fig = px.scatter(df,
                 x=x_axis,
                 y='rating',
                 hover_name='name',
                 title=f'Cereal ratings vs. {x_axis}')

st.plotly_chart(fig)
