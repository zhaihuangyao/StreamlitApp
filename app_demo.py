import streamlit as st
import pandas as pd
import numpy as np

st.title("Uber pickups in NYC")

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')


@st.cache
def load_data(nrows):
    _data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    _data.rename(lowercase, axis="columns", inplace=True)
    _data[DATA_URL] = pd.to_datetime(_data[DATE_COLUMN])
    return _data


data_load_state = st.text('Loading data ...')
data = load_data(10000)

data_load_state.text('Done! (using st.cache)')
