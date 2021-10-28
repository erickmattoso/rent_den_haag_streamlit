import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

data_frame = sns.load_dataset('planets')


def linePlot():
    fig = plt.figure(figsize=(10, 4))
    sns.lineplot(x="distance", y="mass", data=data_frame)
    st.pyplot(fig)


page = st.sidebar.selectbox(
    "Select a Page",
    [
        "Line Plot"
    ]
)
linePlot()
