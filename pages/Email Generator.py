from ListModifiers import create_email
import streamlit as st
import pandas as pd

# Heading
st.title('Email Generator')

# File Uploader for Merged File
st.write("")
st.write("**🤖 LEAD LIST**")
required_cols = ['LINKEDIN_PROFILE__C', 'FIRSTNAME', 'LASTNAME', 'TITLE', 'COMPANY', 'CITY', 'MESSAGE']

merged = st.file_uploader("Required columns: " + ', '.join(required_cols), key="Merged")

me = pd.DataFrame()
if merged is not None:
    me = pd.read_csv(merged)

    if st.button('Show File',key="Merged Button"):
        st.write(me)

# Type in the Capaign Id
st.write("")
st.write("**🔑 OPENAI KEY**")
key = st.text_input('Enter the openai key')

if key != "":
    st.write('The key ID is', key)

# Process and Dowload
st.write("")
st.write("**📥 PROCESS AND DOWNLOAD LEAD LIST**")
process, download = st.columns(2)

# Process
with process: 
    email = pd.DataFrame()
    
    if st.button('Create Lead List'):
        if not me.empty:
            email = create_email(me)
            st.success('Email creation succesfull')
        else:
            st.error('You have to insert the file!')


# Download
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

with download:  
    
    csv = convert_df(email)

    st.download_button(label="Download the Lead List",  data=csv, file_name='LeadList.csv', mime='text/csv')
