import pandas as pd
import numpy as np
import streamlit as st

def improve_quality(df):

    # Reordering the columns
    columns = ['CAMPAIGN_ID_ARRAY__C', 'COMPANY', 'CITY', 'COUNTRY__C', 'EMAIL', 'FIRSTNAME', 'LASTNAME', 'LEADSOURCE', 
               'LINKEDIN_PROFILE__C', 'MOBILEPHONE', 'OFFICE_PHONE__C', 'PHONE', 'RATING', 'REGION__C', 'TITLE', 
               'WEBSITE', 'NOTE', 'MESSAGE', 'EXISTING_ACCOUNT__C']

    improved = df.reindex(columns=columns)

    # Setting np.nan for later analyses
    improved = improved.replace('', np.nan)
    
    # Setting Note column as empty string to use "+" later
    improved['NOTE'] = ''

    return improved

def form_zoominfo(zo, campaign):

    # Dropping columns that aren't needed
    required_cols = ['profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone','Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU']
    zo = zo[required_cols].dropna(how='all', axis=1)

    # Rename the columns
    zo = zo.rename(columns={'profileUrl':'LINKEDIN_PROFILE__C', 'firstName':'FIRSTNAME', 'lastName':'LASTNAME', 
                            'title':'TITLE', 'Email Address':'EMAIL','Mobile phone':'MOBILEPHONE', 
                            'Contact Accuracy Score':'RATING', 'Country':'COUNTRY__C', 
                            'Website':'WEBSITE', 'Company Name':'COMPANY','Within EU':'REGION__C'})

    # Adding columns
    new_cols = {'CAMPAIGN_ID_ARRAY__C':campaign,'CITY': np.nan,'PHONE':np.nan,'OFFICE_PHONE__C':np.nan,'EXISTING_ACCOUNT__C':np.nan,'LEADSOURCE':'demand_gen','MESSAGE':np.nan,'NOTE':np.nan}
    zo = zo.assign(**new_cols)

    # Reordering the columns and clean the data
    zo = improve_quality(zo)

    return zo


def form_cognism(co, campaign):

    # Dropping columns that aren't needed
    required_cols = ['profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input']
    co = co[required_cols].dropna(how='all', axis=1)

    # Rename the columns
    co = co.rename(columns={'profileUrl':'LINKEDIN_PROFILE__C', 'First Name':'FIRSTNAME', 
                            'Last Name':'LASTNAME','Matched Job Title':'TITLE', 'Cognism Email':'EMAIL',
                            'Direct':'PHONE', 'Mobile':'MOBILEPHONE', 'Office':'OFFICE_PHONE__C',
                            'Person Country':'COUNTRY__C', 'Matched Web Site':'WEBSITE', 
                            'Company Name Input':'COMPANY'})

    # Adding columns
    new_cols = {'CAMPAIGN_ID_ARRAY__C':campaign,'CITY': np.nan,'REGION__C':np.nan,'RATING':np.nan,'EXISTING_ACCOUNT__C':np.nan,'LEADSOURCE':'demand_gen','MESSAGE':np.nan,'NOTE':np.nan}
    co = co.assign(**new_cols)

    # Improving quality of the cognism data
    co['PHONE'] = co['PHONE'].str.replace('\t', '')
    co['MOBILEPHONE'] = co['MOBILEPHONE'].str.replace('\t', '')
    co['OFFICE_PHONE__C'] = co['OFFICE_PHONE__C'].str.replace('\t', '')

    co = co.replace(['DNC','TPS','CTPS'], np.nan)

    # Reordering the columns and clean the data
    co = improve_quality(co)

    return co

def form_phantombuster(ph, campaign):

    # Dropping columns that aren't needed
    required_cols = ['query','firstName','lastName','currentJobTitle','emailAddress','currentCompanyName','location','phoneNumber','allSkills']
    ph = ph[required_cols].dropna(how='all', axis=1)

    # Rename the columns
    ph = ph.rename(columns={'query':'LINKEDIN_PROFILE__C', 'firstName':'FIRSTNAME', 'lastName': 'LASTNAME','currentJobTitle':'TITLE', 'emailAddress':'EMAIL', 'phoneNumber':'PHONE','currentCompanyName':'COMPANY', 'website':'WEBSITE', 'location':'CITY', 'allSkills':'MESSAGE'})

    # Adding columns
    new_cols = {'CAMPAIGN_ID_ARRAY__C':campaign,'COUNTRY__C': np.nan,'LEADSOURCE':'demand_gen','MOBILEPHONE':np.nan,'OFFICE_PHONE__C':np.nan,'RATING':np.nan,'REGION__C':np.nan,'NOTE':np.nan,'EXISTING_ACCOUNT__C':np.nan}
    ph = ph.assign(**new_cols)

    # Reordering the columns and clean the data
    ph = improve_quality(ph)

    return ph


def merge(zoominfo, cognism, phantombuster, campaign):
    
    # Modifying the two dataframes
    zoominfo = form_zoominfo(zoominfo, campaign)
    cognism = form_cognism(cognism, campaign)
    phantombuster = form_phantombuster(phantombuster, campaign)
    
    # merged is cognism in the beginning
    merged = cognism.copy() 
    duplic = pd.DataFrame(columns=['LINKEDIN_PROFILE__C', 'EMAIL', 'MOBILEPHONE'])
    
    # iterating through zoominfo to put into merged
    for z_idx, z_row in zoominfo.iterrows():
        
        # Extracting important information from zoominfo row
        linkedIn = z_row["LINKEDIN_PROFILE__C"]
        withInEU = z_row["REGION__C"]
        
        # Searching for same linkedIn profile in cognism/merged
        mask = (merged['LINKEDIN_PROFILE__C'] == linkedIn)
        c_df = merged[mask]
        
        # Has no match and need to be added to merged
        if len(c_df) == 0:
            merged.loc[len(merged)] = z_row.values

            
        # Has one match and information need to be added to row
        elif len(c_df) == 1:
            c_row = c_df.iloc[0]
            
            if withInEU == True: 
                
                # Checking for duplications that might still be useful
                if (c_row['EMAIL'] != z_row['EMAIL']) and not pd.isna(c_row['EMAIL']) and not pd.isna(z_row['EMAIL']):
                    duplic.loc[len(duplic)] = [z_row['LINKEDIN_PROFILE__C'], z_row['EMAIL'], np.nan]
                    
                cognism_numbers = [c_row['MOBILEPHONE'], c_row['OFFICE_PHONE__C'], c_row['PHONE']]
                unique_number = (z_row['MOBILEPHONE'] not in cognism_numbers) and not pd.isna(z_row['MOBILEPHONE'])
                
                if unique_number:
                    if pd.isna(c_row['OFFICE_PHONE__C']): 
                        merged.loc[mask, 'OFFICE_PHONE__C'] = z_row['MOBILEPHONE']
                        
                    elif pd.isna(c_row['PHONE']): 
                        merged.loc[mask, 'PHONE'] = z_row['MOBILEPHONE']
                        
                    elif not pd.isna(c_row['MOBILEPHONE']): 
                        duplic.loc[len(duplic)] = [z_row['LINKEDIN_PROFILE__C'], np.nan, z_row['MOBILEPHONE']]

                # Take cognism value except they are nan
                for col in list(merged.columns):
                    if pd.isna(c_row[col]):
                        merged.loc[mask, col] = z_row[col]
            
            else: 
                # Checking for duplications that might still be useful
                if (c_row['EMAIL'] != z_row['EMAIL']) and not pd.isna(c_row['EMAIL']) and not pd.isna(z_row['EMAIL']):
                    duplic.loc[len(duplic)] = [c_row['LINKEDIN_PROFILE__C'], c_row['EMAIL'], np.nan]
                
                cognism_numbers = [c_row['MOBILEPHONE'], c_row['OFFICE_PHONE__C'], c_row['PHONE']]
                unique_number = (z_row['MOBILEPHONE'] not in cognism_numbers) and not pd.isna(z_row['MOBILEPHONE'])
                
                if unique_number:
                    if pd.isna(c_row['OFFICE_PHONE__C']): 
                        merged.loc[mask, 'OFFICE_PHONE__C'] = z_row['MOBILEPHONE']
                        
                    elif pd.isna(c_row['PHONE']): 
                        merged.loc[mask, 'PHONE'] = z_row['MOBILEPHONE']
                        
                    elif not pd.isna(c_row['MOBILEPHONE']): 
                        duplic.loc[len(duplic)] = [c_row['LINKEDIN_PROFILE__C'], np.nan, c_row['MOBILEPHONE']]
                
                # Take zoominfo value except they are nan
                for col in list(merged.columns):
                    if not pd.isna(z_row[col]):
                        merged.loc[mask, col] = z_row[col]
                        
        # Has more than one match so zoominfo has duplicates    
        else: print("Error: Cognism or Zoominfo has duplicates!!!")


    # Iterate through whole merged dataframe and fill in missing values from ph
    # NOT IDEAL: COMPARING IN MERGED CREATION DIRECTLY
    for idx, row in merged.iterrows():
        linkedIn = row["LINKEDIN_PROFILE__C"]
        mask = (phantombuster['LINKEDIN_PROFILE__C'] == linkedIn)
        match = phantombuster[mask]

        # Insert missing values from ph
        for col in merged.columns:
            if pd.isna(row[col]):
                merged.at[idx, col] = match[col].values[0]

        # Handling duplicate EMAILS
        if (row['EMAIL'] != match['EMAIL'].values[0]) and not pd.isna(match['EMAIL'].values[0]):
            duplic.loc[len(duplic)] = [linkedIn, match['EMAIL'].values[0], np.nan]

        # Handling duplicate NUMBERS
        merged_numbers = [row['MOBILEPHONE'], row['OFFICE_PHONE__C'], row['PHONE']]
        unique_number = (match['PHONE'].values[0] not in merged_numbers) and not pd.isna(match[col].values[0])
                
        if unique_number:
            if pd.isna(row['OFFICE_PHONE__C']): 
                merged.at[idx, 'OFFICE_PHONE__C'] = match['PHONE'].values[0]
                        
            elif pd.isna(row['PHONE']): 
                merged.at[idx, 'PHONE'] = match['PHONE'].values[0]
                        
            elif not pd.isna(c_row['MOBILEPHONE']): 
                duplic.loc[len(duplic)] = [linkedIn, np.nan, match['PHONE'].values[0]]


    # Filling the duplicates in notes 
    # NOT IDEAL: BEST TO NOT EVEN CREATE DF BUT DIRECLTY INSERT IN NOTES
    for idx, row in duplic.iterrows():
        linkedIn = row["LINKEDIN_PROFILE__C"]
        mask = (merged['LINKEDIN_PROFILE__C'] == linkedIn)
        
        if not pd.isna(duplic.at[idx,'EMAIL']): merged.loc[mask, 'NOTE'] += f"Alternative Email: {duplic.at[idx,'EMAIL']} "
        if not pd.isna(duplic.at[idx,'MOBILEPHONE']): merged.loc[mask, 'NOTE'] += f"Alternative Number: {duplic.at[idx,'MOBILEPHONE']} "

    # Improve quality
    merged = merged.replace('', np.nan)
    

    return merged

# Heading
st.title('List Merger')

# File Uploader for Zoominfo
st.write("")
st.write("**🔎 ZOOMINFO CSV FILE**")
zo_requ_cols = ['profileUrl', 'firstName', 'lastName', 'title', 'Email Address', 'Mobile phone','Contact Accuracy Score', 'Country', 'Website', 'Company Name', 'Within EU']

zoominfo = st.file_uploader("Required columns: " + ', '.join(zo_requ_cols), key="Zoominfo")

zo = pd.DataFrame()
if zoominfo is not None:
    zo = pd.read_csv(zoominfo)

    if st.button('Show Content',key="Zoominfo Button"):
        st.write(zo)

# File Uploader for Cognism
st.write("")
st.write("**🌐 COGNISM CSV FILE**")
co_requ_cols = ['profileUrl','First Name', 'Last Name', 'Matched Job Title', 'Cognism Email', 'Direct', 'Mobile', 'Office', 'Person Country', 'Matched Web Site', 'Company Name Input']

cognism = st.file_uploader("Required columns: " + ', '.join(co_requ_cols), key="Cognism")

co = pd.DataFrame
if cognism is not None:
    co = pd.read_csv(cognism)

    if st.button('Show Content', key="Cognism Button"):
        st.write(co)

# File Uploader for Phantombuster
st.write("")
st.write("**👻 PHANTOMBUSTER CSV FILE**")
ph_requ_cols = ['query','firstName','lastName','currentJobTitle','emailAddress','currentCompanyName','location','phoneNumber','allSkills']

phantombuster = st.file_uploader("Required columns: " + ', '.join(ph_requ_cols), key="Phantombuster")

ph = pd.DataFrame()
if phantombuster is not None:
    ph = pd.read_csv(phantombuster)

    if st.button('Show Content', key="Phantombuster Button"):
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
process, download, show = st.columns(3)


# Process
merged = pd.DataFrame()
with process: 
    proc = st.button('Create Lead List')

if proc:
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
    if not merged.empty:
        csv = convert_df(merged)
        st.download_button(label="Download the Lead List",  data=csv, file_name='LeadList.csv', mime='text/csv')

