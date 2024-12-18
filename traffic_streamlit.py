# Import necessary libraries
import streamlit as st
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

st.title('Traffic Volume Predictor')
st.write("Utilize our advanced machine learning algorithm to predict traffic volume")
st.image('traffic_image.gif', use_column_width = True)

@st.cache_resource
def load_model():
    with open("traffic.pickle", "rb") as model_pickle:
        traffic_model = pickle.load(model_pickle)
        model_pickle.close()
    return traffic_model

traffic_model = load_model()

# load the default dataset 
default_df = pd.read_csv('Traffic_Volume.csv')
sample_df = pd.read_csv('traffic_data_user.csv')

# this section was generated by ChatGPT
# convet date_time column to data/time datatype 
default_df['date_time'] = pd.to_datetime(default_df['date_time'])

# create columns to split date_time into numerical features 
default_df['year'] = default_df['date_time'].dt.year
default_df['month'] = default_df['date_time'].dt.month_name()
default_df['weekday'] = default_df['date_time'].dt.day_name()
default_df['hour'] = default_df['date_time'].dt.hour

# drop the original column
default_df = default_df.drop(columns=['date_time', 'year'])


# display sidebar image
st.sidebar.image('traffic_sidebar.jpg',
                         caption = "Traffic Volume Predictor")

# slider that allows user to select an alpha value
a = st.slider('Select alpha value for prediction interval', min_value=0.01, max_value=0.5, step=0.01)

# sidebar header and subheader
st.sidebar.header("Feature Input")
st.sidebar.write("You can either upload your data file or maually enter diamond features.")

with st.sidebar.expander("Option 1: Upload CSV File"):
    file_upload = st.file_uploader('Upload File')
    st.write(sample_df.head())

if file_upload is None:
     pass
else:
    upload_df = pd.read_csv(file_upload)
    upload_encoded = default_df.copy()
    upload_encoded = upload_encoded.drop(columns=['traffic_volume'])
    upload_encoded = pd.concat([upload_encoded, upload_df], ignore_index=True)
    upload_dummies = pd.get_dummies(upload_encoded)
    upload_clean = upload_dummies.tail(len(upload_df))
    prediction, intervals = traffic_model.predict(upload_clean, alpha = a)
    upload_clean['Traffic Volume Prediction'] = prediction
    upload_clean['Lower Limit'] = np.maximum(0, intervals[:, 0])
    upload_clean['Upper Limit'] = intervals[:, 1]
    upload_clean = upload_clean.drop(upload_clean.columns[5:46], axis=1)
    st.write("## Predicted Results with ", (1-a)*100, "% Confidence Interval")
    st.write(upload_clean)
    
# 5-25 

with st.sidebar.expander("Option 2: Fill out Form"):
        with st.form("Enter the traffic details manualy using the form below"):
            st.write("Enter the traffic details manualy using the form below")
            holiday = st.selectbox('Choose whether today is designated as a holiday or not', options=default_df['holiday'].unique())
            temp = st.number_input('Average temperature in Kelvin', min_value=default_df['temp'].min(), max_value=default_df['temp'].max(), step=0.01)
            rain = st.number_input('Amount in mm of rain that occurred in the hour', min_value=default_df['rain_1h'].min(), max_value=default_df['rain_1h'].max(), step=0.01)
            snow = st.number_input('Amount in mm of snow that occurred in the hour', min_value=default_df['snow_1h'].min(), max_value=default_df['snow_1h'].max(), step=0.01)
            cloud = st.number_input('Percentage of cloud cover', min_value=default_df['clouds_all'].min(), max_value=default_df['clouds_all'].max(), step=1)
            weather = st.selectbox('Choose the current weather', options=default_df['weather_main'].unique())
            month = st.selectbox('Choose month', options=default_df['month'].unique())
            day = st.selectbox('Choose the day of the week', options=default_df['weekday'].unique())
            hour = st.selectbox('Choose hour', options=default_df['hour'].unique())
            submit_button = st.form_submit_button("Submit Form Data")

if file_upload is None:
    # Encode the inputs for model prediction
    encode_df = default_df.copy()
    encode_df = encode_df.drop(columns=['traffic_volume'])

    # Combine the list of user data as a row to default_df
    encode_df.loc[len(encode_df)] = [holiday, temp, rain, snow, cloud, weather, month, day, hour]

    # Create dummies for encode_df
    encode_dummy_df = pd.get_dummies(encode_df)

    # Extract encoded user data
    user_encoded_df = encode_dummy_df.tail(1)

    # Get the prediction with its intervals
    prediction, intervals = traffic_model.predict(user_encoded_df, alpha = a)
    pred_value = prediction[0]
    lower_limit = intervals[:, 0]
    upper_limit = intervals[:, 1]

    # Ensure limits are within [0, 1]
    lower_limit = max(0, lower_limit[0][0])
    upper_limit = max(0, upper_limit[0][0])

    # show prediction on the app
    st.write('## Predicting Traffic Volume...')

    # Display results using metric card
    st.metric(label = "Predicted Volume", value = f"{pred_value:.2f}")
    st.write("With a", 1-a, f"% confidence interval: [{lower_limit:.2f}, {upper_limit:.2f}]")


tab1, tab2, tab3, tab4 = st.tabs(["Feature Importance", "Histogram of Residuals", "Scatter Plot of Predicted vs Actual Values", "Upper Prediction Limit"])
feature_image = 'feature_imp.svg'
residual = 'residual_plot.svg'
scatter = 'pred_vs_actual.svg'
upper_pred = 'coverage.svg'

with tab1:
    st.write("Feature Importance")
    st.image(feature_image)
    st.caption("Features used in this prediction are ranked by relative importance.")
with tab2:
    st.write("Histogram of Residuals")
    st.image(residual)
with tab3:
    st.write("Scatter Plot of Predicted vs Actual Values")
    st.image(scatter)
with tab4:
    st.write("Upper Prediction Limit")
    st.image(upper_pred)