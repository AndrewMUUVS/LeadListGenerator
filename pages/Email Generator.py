import streamlit as st
import pandas as pd
import openai
import time

def create_email(df, openai_key):
    openai.api_key = openai_key

    count = 0
    for idx, row in df.iterrows():
    
        # Template for AI
        if not pd.isna(row['FIRSTNAME']) and not pd.isna(row['CITY']) and not pd.isna(row['TITLE']) and not pd.isna(row['MESSAGE']):
        
            # Template for AI
            comma = ","
            template = f"Hey {row['FIRSTNAME']}, I hope your day is going well in {row['CITY'].split(comma)[0]}. The reason for my message is that I noticed your experience as an {row['TITLE'].split(comma)[0]} as well as with [] and []."
    
            # create a prompt
            skills = row['MESSAGE']
            prompt = f"Extract two different techincal data analytics skills from a skillset. \
                        Prioritize SQL, dbt, Snowflake. \
                        Machine Learning, Deep Learning, C++, Java or Data Visualization should not be mentioned.\
                        Give no descriptions and list the two skills with a comma between them.\
                        The skillset: {skills}."

            # generate text using the GPT-3 language model
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=2000,
                n=1,
                stop=None,
                temperature=0.7,
            )

            # print the generated text and save it
            skills = response.choices[0].text
            skills = skills.strip()
            print()
            print("Extracted skills: ", skills)
    
            # Waiting if exceeded request limits
            count = count + 1
            if count == 60:
                count = 0
                time.sleep(70)
        
            # Fill in the template
            comma = ","
            template = f"Hey {row['FIRSTNAME']}, I hope your day is going well in {row['CITY'].split(comma)[0]}. The reason for my message is that I noticed your experience as an {row['TITLE'].split(comma)[0]} as well as with {skills.split(comma)[0]} and{skills.split(comma)[1]}."
        
            # Insert the text and print it
            df.loc[idx, 'MESSAGE'] = template
            print(idx, df.loc[idx, 'MESSAGE'])


        elif not pd.isna(row['FIRSTNAME']) and not pd.isna(row['CITY']) and not pd.isna(row['TITLE']):
            # Fill in the template
            comma = ","
            template = f"Hey {row['FIRSTNAME']}, I hope your day is going well in {row['CITY'].split(comma)[0]}. The reason for my message is that I noticed your experience as an {row['TITLE'].split(comma)[0]}."
        
            # Insert the text and print it
            df.loc[idx, 'MESSAGE'] = template
            print(idx, df.loc[idx, 'MESSAGE'])

    return df

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
            email = create_email(me, key)
            create_email()
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
