#import numpy as np
import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)

st.title('My Cool Name App')

with st.sidebar:
    input_name = st.text_input('Enter a name:')
    input_year = st.slider('Select a year:', min_value=1880, max_value=2023, value=2000)
    n_names = st.radio('Number of names per sex:', [3, 4, 5, 6, 10])


# Set up tabs
tab1, tab2, tab3 = st.tabs(['Names', 'Year', 'One Hit Wonders'])

# Name Trends
with tab1:
    name_data = data[data['name'] == input_name].copy()
    fig = px.line(name_data, x='year', y='count', color='sex')

    st.plotly_chart(fig)


# Top Names Plot
with tab2:
    fig2 = top_names_plot(data, n=n_names, year=input_year)
    
    st.plotly_chart(fig2)

    st.write('Unique Names Table')
    names_table = unique_names_summary(data, input_year)
    st.dataframe(names_table)


# One Hit Wonders
with tab3:
    ohw_year = st.slider('Select a year:', min_value=1880, max_value=2023, value=2000)
    result = one_hit_wonders(ohw_data, ohw_year)

    st.write(result["message"])  # Display the main message
    
    if result["data"] is not None:
        # Display counts and most common names
        st.write(f"Number of female one-hit wonders: {result['female_count']}")
        st.write(f"Number of male one-hit wonders: {result['male_count']}")
        st.write(f"Most common female one-hit wonder: {result['most_common_female']}")
        st.write(f"Most common male one-hit wonder: {result['most_common_male']}")
        
        # Display the table of one-hit wonders
        st.dataframe(result["data"])


