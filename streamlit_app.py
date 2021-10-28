import streamlit as st
import seaborn as sns

penguins = sns.load_dataset("penguins")

st.title("Hello")
fig = sns.pairplot(penguins, hue="species")
st.pyplot(fig)
