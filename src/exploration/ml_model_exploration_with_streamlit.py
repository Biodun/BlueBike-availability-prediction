import streamlit as st
import pandas as pd 
import numpy as np

st.title("Debugging my ML model")

data_df = pd.read_csv(r'/home/aiwayemi/data_science/Data-Science-Projects/bluebike_availability_prediction/data/processed/hourly_ridership_data/station_67__2017_ridership_data.csv')

default_columns = ['total_trips', 'num_subscriber_trips', 'num_customer_trips', 'hour_of_day', 'day_of_week', 'day', 'month', 'is_weekend', 'hour_sine', 'hour_cos', 'month_sine', 'month_cos', 'day_of_week_sine', 'day_of_week_cos', 'summary', 'temperature', 'humidity', 'pressure', 
'windSpeed', 'precipIntensity', 'visibility', 'cloudCover', 'uvIndex']

# columns_for_display = st.multiselect(label='Select which columns to display', options = data_df.columns, )
# st.write(f"You selected the following columns:\n{columns_for_display}")

n_samples = st.slider("Select how much of the training data data to display", min_value=10, max_value=len(data_df), step=10 )
st.write(f"Showing {n_samples} rows of data")
st.write(data_df[default_columns].head(n_samples))

# Plot time series of the data
x_axis = st.selectbox('Select X axis variable', options=default_columns)
y_axis = st.selectbox('Select Y axis variable', options=default_columns)

st.line_chart(data=data_df[])


# # Using magic commands
# df = pd.DataFrame({
#     'first column': [1, 2, 3, 4],
#     'second column': [10, 20, 30, 40]
# })

# df
# if st.checkbox('Show line chart'):
#     # Practice creating line charts
#     chart_data = pd.DataFrame(
#         np.random.randn(20, 3),
#         columns=['a', 'b', 'c']
#     )
#     st.line_chart(chart_data)

# if st.checkbox("Show map"):
#     map_data = pd.DataFrame(
#         np.random.randn(1000, 2) / [50, 50] + [44.48, -73.21],
#         columns=['lat', 'lon']
#     )

#     st.map(map_data)

# option = st.sidebar.selectbox('Choose a number', df['first column'])

# 'You selected: ', option