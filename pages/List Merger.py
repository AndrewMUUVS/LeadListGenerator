import pandas as pd
import numpy as np
import streamlit as st
from ListModify import merge

# Heading
st.title('Lead List Generator')

# File Uploader for Zoominfo
st.write("")
st.write("**🔎 ZOOMINFO CSV FILE**")
zo_requ_cols = ['profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone','Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU']

zoominfo = st.file_uploader("Required columns: " + ', '.join(zo_requ_cols), key="Zoominfo")

zo = pd.DataFrame()
if zoominfo is not None:
    zo = pd.read_csv(zoominfo)

    if st.button('Show File',key="Zoominfo Button"):
        st.write(zo)

# File Uploader for Cognism
st.write("")
st.write("**🌐 COGNISM CSV FILE**")
co_requ_cols = ['profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input']

cognism = st.file_uploader("Required columns: " + ', '.join(co_requ_cols), key="Cognism")

co = pd.DataFrame
if cognism is not None:
    co = pd.read_csv(cognism)

    if st.button('Show File', key="Cognism Button"):
        st.write(co)

# File Uploader for Phantombuster
st.write("")
st.write("**👻 PHANTOMBUSTER CSV FILE**")
ph_requ_cols = ['query','firstName','lastName','currentJobTitle','emailAddress','currentCompanyName','location','phoneNumber','allSkills']

phantombuster = st.file_uploader("Required columns: " + ', '.join(ph_requ_cols), key="Phantombuster")

ph = pd.DataFrame()
if phantombuster is not None:
    ph = pd.read_csv(phantombuster)

    if st.button('Show File', key="Phantombuster Button"):
        st.write(ph)


# Type in the Capaign Id
st.write("")
st.write("**📝 CAMPAIGN ID**")
campaign = st.text_input('Enter the Campaign ID', "campaign_id")

if campaign != "campaign_id":
    st.write('The Campaign ID is', campaign)


# Process and Dowload
st.write("")
st.write("**📥 PROCESS AND DOWNLOAD LEAD LIST**")
process, download = st.columns(2)


# Process
with process: 
    merged = pd.DataFrame()
    
    if st.button('Create Lead List'):
        if not zo.empty and not co.empty and not ph.empty:
            merged = merge(zo, co, ph, campaign)
            st.success('Merge was succesfull')
        else:
            st.error('You have to insert the files!')


# Download
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

with download:  
    
    csv = convert_df(merged)

    st.download_button(label="Download the Lead List",  data=csv, file_name='LeadList.csv', mime='text/csv')
